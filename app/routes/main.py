from flask import Blueprint, render_template, redirect, url_for, request, flash, session, abort, current_app
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
                current_app.logger.info(f'Successful login: user={state_id}')
                return redirect(url_for('main.dashboard'))
            else:
                current_app.logger.warning(f'Failed login attempt: state_id={state_id}, reason=invalid_credentials')
                flash('Invalid state ID or password')
        except ValidationError as e:
            current_app.logger.warning(f'Failed login attempt: state_id={request.form.get("state_id")}, reason=validation_error, error={str(e)}')
            flash(str(e))

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    """Logout user"""
    user_id = current_user.get_id()
    session.clear()
    logout_user()
    current_app.logger.info(f'User logged out: user={user_id}')
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
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error in dismiss_approval: attempt_id={attempt_id}, error={str(e)}')
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
            # If returning to revise, set status back to in_progress and reset to question 1
            if attempt.status == 'needs_revision':
                attempt.status = 'in_progress'
                attempt.current_question_index = 0  # Start from beginning for revisions

            # If question_order already exists in database, use it; otherwise generate new
            if attempt.question_order:
                question_order = attempt.question_order
            else:
                # Generate question order for existing attempts that don't have it
                if assessment.randomize_questions:
                    questions = list(assessment.questions)
                    random.shuffle(questions)
                else:
                    questions = sorted(assessment.questions, key=lambda q: q.question_order)
                question_order = [q.question_id for q in questions]
                attempt.question_order = question_order
        else:
            # Generate question order for new attempts
            if assessment.randomize_questions:
                questions = list(assessment.questions)
                random.shuffle(questions)
            else:
                questions = sorted(assessment.questions, key=lambda q: q.question_order)
            question_order = [q.question_id for q in questions]

            previous_attempts = AssessmentAttempt.query.filter_by(
                state_id=current_user.state_id,
                assessment_id=assessment.assessment_id
            ).count()

            # Create new attempt with question order stored in database
            attempt = AssessmentAttempt(
                state_id=current_user.state_id,
                assessment_id=assessment.assessment_id,
                attempt_number=previous_attempts + 1,
                status='in_progress',
                started_at=datetime.now(timezone.utc),
                question_order=question_order,
                current_question_index=0
            )

            db.session.add(attempt)

        db.session.commit()

        # Store in session for performance (acts as cache)
        session['current_attempt_id'] = attempt.attempt_id
        session['question_order'] = question_order
        session['current_question_index'] = attempt.current_question_index

        # Redirect to first question
        first_question_id = question_order[attempt.current_question_index]
        return redirect(url_for('main.show_question', question_id=first_question_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error in start_assessment: user={current_user.state_id}, step={step_number}, error={str(e)}')
        flash('An error occurred while starting the assessment. Please try again.')
        return redirect(url_for('main.dashboard'))


@main.route('/question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def show_question(question_id):
    """Display single question"""
    # Get attempt_id from session or find in-progress attempt
    attempt_id = session.get('current_attempt_id')

    if not attempt_id:
        # Session expired - try to recover from database
        attempt = AssessmentAttempt.query.filter_by(
            state_id=current_user.state_id,
            status='in_progress'
        ).first()

        if not attempt:
            flash('Please start the assessment from the beginning.')
            return redirect(url_for('main.dashboard'))

        attempt_id = attempt.attempt_id
        session['current_attempt_id'] = attempt_id
    else:
        attempt = AssessmentAttempt.query.get(attempt_id)

        if not attempt:
            flash('Assessment session not found. Please start again.')
            return redirect(url_for('main.dashboard'))

    question = Question.query.get(question_id)
    if not question:
        flash('Question not found.')
        return redirect(url_for('main.dashboard'))

    # Get question order from database (source of truth)
    question_order = attempt.question_order or session.get('question_order', [])

    # Determine the actual index of the current question in the order
    # This ensures correct tracking whether user navigates forward or backward
    try:
        current_index = question_order.index(question_id)
    except ValueError:
        # Question not in order - shouldn't happen, but handle gracefully
        flash('Invalid question for this assessment.')
        return redirect(url_for('main.dashboard'))

    # Update database and session cache with the actual index
    if attempt.current_question_index != current_index:
        try:
            attempt.current_question_index = current_index
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating question index: user={current_user.state_id}, question_id={question_id}, error={str(e)}')
            # Continue anyway - this is not critical

    session['question_order'] = question_order
    session['current_question_index'] = current_index

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

            # Move to next question or finish
            next_index = current_index + 1
            if next_index < len(question_order):
                # Commit the response (index will be updated when next question loads)
                db.session.commit()
                next_question_id = question_order[next_index]
                return redirect(url_for('main.show_question', question_id=next_question_id))
            else:
                # Assessment complete - commit the response
                db.session.commit()
                return redirect(url_for('main.assessment_complete'))

        except ValidationError as e:
            flash(str(e))
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f'Database error in show_question: user={current_user.state_id}, question_id={question_id}, error={str(e)}')
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
                           saved_response=saved_response,
                           question_order=question_order,
                           is_revision=(attempt.attempt_number > 1)
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
                current_app.logger.info(f'Assessment submitted: user={current_user.state_id}, attempt_id={attempt_id}')
            except SQLAlchemyError as e:
                db.session.rollback()
                current_app.logger.error(f'Database error in assessment_complete: user={current_user.state_id}, attempt_id={attempt_id}, error={str(e)}')
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
    current_app.logger.warning(f'404 error: path={request.path}, user={current_user.get_id() if current_user.is_authenticated else "anonymous"}')
    return render_template('404.html'), 404


@main.app_errorhandler(403)
def page_forbidden(error):
    """Handle 403 errors with a custom page"""
    current_app.logger.warning(f'403 error: path={request.path}, user={current_user.get_id() if current_user.is_authenticated else "anonymous"}')
    return render_template('403.html'), 403
