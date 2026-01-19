from flask import Blueprint, render_template, redirect, url_for, request, flash, session, abort, current_app
from flask_login import login_user, login_required, current_user
from werkzeug.security import check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from functools import wraps
from datetime import datetime, timezone

from app import db, limiter
from app.models import User, Admin, Assessment, AssessmentAttempt, Response, Question
from app.validators import (
    ValidationError,
    validate_admin_id,
    validate_password,
    validate_decision,
    validate_text_response
)

admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Used to restrict access to certain routes to admin only"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the current user is an admin
        if not isinstance(current_user, Admin):
            current_app.logger.warning(f'Unauthorized admin access attempt: user={current_user.get_id() if current_user.is_authenticated else "anonymous"}')
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


@admin.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        try:
            admin_id = validate_admin_id(request.form.get('admin_id'))
            password = validate_password(request.form.get('password'))

            admin = Admin.query.get(admin_id)

            if admin and admin.is_active and check_password_hash(admin.password_hash, password):
                session.clear()
                login_user(admin)
                session['user_type'] = 'admin'
                current_app.logger.info(f'Successful admin login: admin_id={admin_id}')
                return redirect(url_for('admin.admin_dashboard'))
            else:
                current_app.logger.warning(f'Failed admin login attempt: admin_id={admin_id}, reason=invalid_credentials')
                flash('Invalid admin ID or password')
        except ValidationError as e:
            current_app.logger.warning(f'Failed admin login attempt: admin_id={request.form.get("admin_id")}, reason=validation_error, error={str(e)}')
            flash(str(e))

    return render_template('admin_login.html')


@admin.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard showing pending assessments"""
    # Get all submitted attempts that need review (status = 'submitted')
    pending_attempts = AssessmentAttempt.query.filter_by(
        status='submitted'
    ).options(
        joinedload(AssessmentAttempt.user),
        joinedload(AssessmentAttempt.assessment).joinedload(Assessment.step)
    ).order_by(AssessmentAttempt.submitted_at.desc()).all()

    return render_template('admin_dashboard.html', pending_attempts=pending_attempts)


@admin.route('/review/<int:attempt_id>', methods=['GET', 'POST'])
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


@admin.route('/view/<int:attempt_id>')
@login_required
@admin_required
def view_attempt(attempt_id):
    """View any assessment attempt in read-only mode"""
    # Get attempt with eager loading to avoid N+1 queries
    attempt = AssessmentAttempt.query.options(
        joinedload(AssessmentAttempt.user),
        joinedload(AssessmentAttempt.assessment).joinedload(Assessment.step),
        joinedload(AssessmentAttempt.reviewer)
    ).get_or_404(attempt_id)

    # Get all responses for this attempt
    responses = Response.query.filter_by(attempt_id=attempt_id).all()
    responses_by_question = {response.question_id: response for response in responses}

    # Get questions in order
    questions = Question.query.filter_by(
        assessment_id=attempt.assessment_id
    ).order_by(Question.question_order).all()

    # Get all attempts for this user/assessment for context
    all_attempts = AssessmentAttempt.query.filter_by(
        state_id=attempt.state_id,
        assessment_id=attempt.assessment_id
    ).order_by(AssessmentAttempt.attempt_number).all()

    return render_template('view_attempt.html',
                           attempt=attempt,
                           questions=questions,
                           responses_by_question=responses_by_question,
                           all_attempts=all_attempts)


@admin.route('/review/<int:attempt_id>/submit', methods=['POST'])
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
        attempt.reviewed_at = datetime.now(timezone.utc)
        attempt.clinician_notes = clinician_notes

        # Save changes
        db.session.commit()
        current_app.logger.info(f'Assessment review submitted: admin={current_user.admin_id}, attempt_id={attempt_id}, decision={decision}')
    except ValidationError as e:
        flash(str(e))
        return redirect(url_for('admin.review_attempt', attempt_id=attempt_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Database error in submit_review: admin={current_user.admin_id}, attempt_id={attempt_id}, error={str(e)}')
        flash('An error occurred while saving the review. Please try again.')
        return redirect(url_for('admin.review_attempt', attempt_id=attempt_id))

    return redirect(url_for('admin.admin_dashboard'))