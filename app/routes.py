from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, limiter
from app.models import User, Step, Assessment, Question, Response, AssessmentAttempt, Admin
import random
from flask import session
from datetime import datetime
from functools import wraps
from flask import abort
from app.validators import (
    ValidationError,
    validate_state_id,
    validate_admin_id,
    validate_password,
    validate_decision,
    validate_integer_id,
    validate_text_response
)


def admin_required(f):
    """Used to restrict access to certain routes to admin only"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the current user is an admin
        if not isinstance(current_user, Admin):
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


# Create a blueprint for routes
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page - redirects to log in or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Login page"""
    if request.method == 'POST':
        try:
            # Validate inputs
            state_id = validate_state_id(request.form.get('state_id'))
            password = validate_password(request.form.get('password'))

            user = User.query.get(state_id)

            if user and check_password_hash(user.password_hash, password):
                session.clear()
                login_user(user)
                session['user_type'] = 'participant'
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid state ID or password')
        except ValidationError as e:
            flash(str(e))

    return render_template('login.html')


@main.route('/admin/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        try:
            admin_id = validate_admin_id(request.form.get('admin_id'))
            password = validate_password(request.form.get('password'))

            admin = Admin.query.get(admin_id)

            if admin and check_password_hash(admin.password_hash, password):
                session.clear()
                login_user(admin)
                session['user_type'] = 'admin'
                return redirect(url_for('main.admin_dashboard'))
            else:
                flash('Invalid admin ID or password')
        except ValidationError as e:
            flash(str(e))

    return render_template('admin_login.html')


@main.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard showing pending assessments"""
    # Get all submitted attempts that need review (status = 'submitted')
    pending_attempts = AssessmentAttempt.query.filter_by(
        status='submitted'
    ).order_by(AssessmentAttempt.submitted_at.desc()).all()

    return render_template('admin_dashboard.html', pending_attempts=pending_attempts)


@main.route('/admin/review/<int:attempt_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def review_attempt(attempt_id):
    """Review a participant's assessment attempt"""
    # Get the attempt
    attempt = AssessmentAttempt.query.get_or_404(attempt_id)

    # Get all responses for this attempt
    responses = Response.query.filter_by(attempt_id=attempt_id).all()

    # Organize responses by question for template access
    responses_by_question = {response.question_id: response for response in responses}

    # Get all questions for this assessment
    questions = Question.query.filter_by(
        assessment_id=attempt.assessment_id
    ).order_by(Question.question_order).all()

    return render_template('review_attempt.html',
                           attempt=attempt,
                           questions=questions,
                           responses_by_question=responses_by_question)


@main.route('/admin/review/<int:attempt_id>/submit', methods=['POST'])
@login_required
@admin_required
def submit_review(attempt_id):
    try:
        # Get the attempt
        attempt = AssessmentAttempt.query.get_or_404(attempt_id)

        # Get form data
        decision = validate_decision(request.form.get('decision'))
        clinician_notes = validate_text_response(request.form.get('clinician_notes'), "Clinician note", max_length=5000)

        # Update the attempt based on decision
        if decision == 'approve':
            attempt.status = 'approved'

            # Advance the user to the next step
            user = User.query.get(attempt.state_id)
            user.current_step += 1

            flash('Assessment approved! Participant can proceed to the next step', 'success')

        elif decision == 'needs_revision':
            attempt.status = 'needs_revision'
            flash('Participant notified that revision is needed.', 'warning')

        # Set review metadata
        attempt.reviewed_by = current_user.admin_id
        attempt.reviewed_at = datetime.utcnow()
        attempt.clinician_notes = clinician_notes

        # Save changes
        db.session.commit()
    except ValidationError as e:
        flash(str(e))
        return redirect(url_for('main.review_attempt', attempt_id=attempt_id))

    return redirect(url_for('main.admin_dashboard'))


@main.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('main.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing progress"""
    # Redirect to the admin dashboard if the user is an admin
    if isinstance(current_user, Admin):
        return redirect(url_for('main.admin_dashboard'))

    # Get current step
    current_step = Step.query.filter_by(step_number=current_user.current_step).first()

    # Get the assessment for the current step
    assessment = Assessment.query.filter_by(step_id=current_step.step_id).first() if current_step else None

    # Get user's most recent attempt for this assessment
    current_attempt = None
    if assessment:
        current_attempt = AssessmentAttempt.query.filter_by(
            state_id=current_user.state_id,
            assessment_id=assessment.assessment_id
        ).order_by(AssessmentAttempt.attempt_number.desc()).first()

    return render_template('dashboard.html',
                           current_step=current_step,
                           current_attempt=current_attempt)


@main.route('/assessment/<int:step_number>')
@login_required
def start_assessment(step_number):
    """Start an assessment for a specific step"""
    # Check if user is on this step
    if step_number != current_user.current_step:
        flash(f'You must complete Step {current_user.current_step} first.')
        return redirect(url_for('main.dashboard'))

    # Get the assessment for this step
    step = Step.query.filter_by(step_number=step_number).first()
    if not step:
        flash('Step not found.')
        return redirect(url_for('main.dashboard'))

    assessment = Assessment.query.filter_by(step_id=step.step_id).first()
    if not assessment:
        flash('No assessment available for this step yet.')
        return redirect(url_for('main.dashboard'))

    # Get questions (randomized or ordered)
    if assessment.randomize_questions:
        questions = list(assessment.questions)
        random.shuffle(questions)
    else:
        questions = sorted(assessment.questions, key=lambda q: q.question_order)

    # Store question order in session for consistency
    session['question_order'] = [q.question_id for q in questions]
    session['current_question_index'] = 0

    # Count previous attempts for this assessment
    previous_attempts = AssessmentAttempt.query.filter_by(
        state_id=current_user.state_id,
        assessment_id=assessment.assessment_id
    ).count()

    # Create new attempt
    attempt = AssessmentAttempt(
        state_id=current_user.state_id,
        assessment_id=assessment.assessment_id,
        attempt_number=previous_attempts + 1,
        status='in_progress',
        started_at=datetime.utcnow()
    )

    db.session.add(attempt)
    db.session.commit()

    # Store attempt_id in session so response can link to it
    session['current_attempt_id'] = attempt.attempt_id

    # Redirect to first question
    first_question_id = questions[0].question_id
    return redirect(url_for('main.show_question', question_id=first_question_id))


@main.route('/question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def show_question(question_id):
    """Display single question"""
    # Safety check to ensure user started assessment properly
    if 'current_attempt_id' not in session:
        flash('Please start the assessment from the beginning.')
        return redirect(url_for('main.dashboard'))

    question = Question.query.get(question_id)
    if not question:
        flash('Question not found.')
        return redirect(url_for('main.dashboard'))

    # Get question order from session
    question_order = session.get('question_order', [])
    current_index = session.get('current_question_index', 0)

    if request.method == 'POST':
        try:
            # Save the response
            if question.question_type == 'multiple_choice':
                selected_option_id = validate_integer_id(request.form.get('selected_option'))
                response = Response(
                    attempt_id=session['current_attempt_id'],
                    question_id=question_id,
                    selected_option_id=selected_option_id
                )
            else:
                response_text = validate_text_response(request.form.get('response_text'), "Response")
                response = Response(
                    attempt_id=session['current_attempt_id'],
                    question_id=question_id,
                    response_text=response_text
                )

            db.session.add(response)
            db.session.commit()

            # Move to next question or finish
            next_index = current_index + 1
            if next_index < len(question_order):
                session['current_question_index'] = next_index
                next_question_id = question_order[next_index]
                return redirect(url_for('main.show_question', question_id=next_question_id))
            else:
                # Assessment complete
                return redirect(url_for('main.assessment_complete'))

        except ValidationError as e:
            flash(str(e))

    # Calculate progress
    total_questions = len(question_order)
    progress = f"Question {current_index + 1} of {total_questions}"

    return render_template('question.html',
                           question=question,
                           progress=progress,
                           current_index=current_index,
                           total_questions=total_questions
                           )


@main.route('/assessment/complete')
@login_required
def assessment_complete():
    """Assessment completion page"""

    # Get the current step from the session
    attempt_id = session.get('current_attempt_id')

    if attempt_id:
        # Find the attempt in the database
        attempt = AssessmentAttempt.query.get(attempt_id)

        if attempt:
            # Mark as submitted (no longer in_progress)
            attempt.status = 'submitted'
            attempt.submitted_at = datetime.utcnow()
            db.session.commit()

    # Clear session data
    session.pop('question_order', None)
    session.pop('current_question_index', None)
    session.pop('current_attempt_id', None)

    return render_template('assessment_complete.html')
