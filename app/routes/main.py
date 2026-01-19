from flask import Blueprint, render_template, redirect, url_for, request, flash, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from app import db, limiter
from app.models import User, Step, Assessment, Question, Response, AssessmentAttempt, Admin
from app.validators import (
    ValidationError,
    validate_state_id,
    validate_password,
    validate_integer_id,
    validate_text_response
)
import random
from datetime import datetime, timezone

# Create blueprint
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page - redirects to log in or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def login():
    """Login page"""
    if request.method == 'POST':
        try:
            # Validate inputs
            state_id = validate_state_id(request.form.get('state_id'))
            password = validate_password(request.form.get('password'))

            user = User.query.get(state_id)

            if user and user.is_active and check_password_hash(user.password_hash, password):
                session.clear()
                login_user(user)
                session['user_type'] = 'participant'
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid state ID or password')
        except ValidationError as e:
            flash(str(e))

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    """Logout user"""
    session.clear()
    logout_user()
    return redirect(url_for('main.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing progress"""
    # Redirect to the admin dashboard if the user is an admin
    if isinstance(current_user, Admin):
        return redirect(url_for('admin.admin_dashboard'))

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

    # Get all previous completed attempts for history
    previous_attempts = []
    if current_user.current_step > 1:
        for step_num in range(1, current_user.current_step):
            step = Step.query.filter_by(step_number=step_num).first()
            if step:
                assessment = Assessment.query.filter_by(step_id=step.step_id).first()
                if assessment:
                    attempt = AssessmentAttempt.query.filter_by(
                        state_id=current_user.state_id,
                        assessment_id=assessment.assessment_id
                    ).order_by(AssessmentAttempt.attempt_number.desc()).first()
                    if attempt and attempt.status in ['approved', 'needs_revision']:
                        previous_attempts.append({
                            'step': step,
                            'attempt': attempt
                        })

    # Check for unviewed approval
    unviewed_approval = None
    for prev_attempt_data in previous_attempts:
        attempt = prev_attempt_data['attempt']
        if attempt.status == 'approved' and not attempt.approval_viewed:
            unviewed_approval = prev_attempt_data
            break

    return render_template('dashboard.html',
                           current_step=current_step,
                           current_attempt=current_attempt,
                           previous_attempts=previous_attempts,
                           unviewed_approval=unviewed_approval
                           )


@main.route('/dismiss-approval/<int:attempt_id>', methods=['POST'])
@login_required
def dismiss_approval(attempt_id):
    """Mark an approval notification is viewed"""
    attempt = AssessmentAttempt.query.get_or_404(attempt_id)

    # Verify this attempt belongs to the current user
    if attempt.state_id != current_user.state_id:
        abort(403)

    try:
        attempt.approval_viewed = True
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred while dismissing the notification. Please try again.')

    return redirect(url_for('main.dashboard'))


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

    # Check for existing in-progress or needs-revision attempt
    existing_attempt = AssessmentAttempt.query.filter_by(
        state_id=current_user.state_id,
        assessment_id=assessment.assessment_id
    ).filter(
        AssessmentAttempt.status.in_(['in_progress', 'needs_revision'])
    ).first()

    try:
        if existing_attempt:
            attempt = existing_attempt
            # If returning to revise, set status back to in_progress
            if attempt.status == 'needs_revision':
                attempt.status = 'in_progress'
        else:
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
                started_at=datetime.now(timezone.utc)
            )

            db.session.add(attempt)

        db.session.commit()

        # Store attempt_id in session so response can link to it
        session['current_attempt_id'] = attempt.attempt_id

        # Redirect to first question
        first_question_id = questions[0].question_id
        return redirect(url_for('main.show_question', question_id=first_question_id))
    except SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred while starting the assessment. Please try again.')
        return redirect(url_for('main.dashboard'))


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
            # Check if a response already exists for this attempt/question combo
            response = Response.query.filter_by(
                attempt_id = session['current_attempt_id'],
                question_id=question_id
            ).first()

            if question.question_type == 'multiple_choice':
                selected_option_id = validate_integer_id(request.form.get('selected_option'))

                if response:
                    response.selected_option_id = selected_option_id
                else:
                    response = Response(
                        attempt_id=session['current_attempt_id'],
                        question_id=question_id,
                        selected_option_id=selected_option_id
                    )
                    db.session.add(response)
            else:
                response_text = validate_text_response(request.form.get('response_text'),"Response")

                if response:
                    response.response_text = response_text
                else:
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
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while saving your response. Please try again.')

    # Fetch existing response to pre-fill the form
    saved_response = Response.query.filter_by(
        attempt_id=session['current_attempt_id'],
        question_id=question_id
    ).first()

    # Calculate progress
    total_questions = len(question_order)
    progress = f"Question {current_index + 1} of {total_questions}"

    return render_template('question.html',
                           question=question,
                           progress=progress,
                           current_index=current_index,
                           total_questions=total_questions,
                           saved_response=saved_response
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
            try:
                # Mark as submitted (no longer in_progress)
                attempt.status = 'submitted'
                attempt.submitted_at = datetime.now(timezone.utc)
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
                flash('An error occurred while submitting the assessment. Please contact support.')

    # Clear session data
    session.pop('question_order', None)
    session.pop('current_question_index', None)
    session.pop('current_attempt_id', None)

    return render_template('assessment_complete.html')


# Error Handlers
@main.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 errors with a custom page"""
    return render_template('404.html'), 404


@main.app_errorhandler(403)
def page_forbidden(error):
    """Handle 403 errors with a custom page"""
    return render_template('403.html'), 403
