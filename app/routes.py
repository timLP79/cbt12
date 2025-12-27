from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User, Step, Assessment, Question, Response
import random
from flask import session


# Create a blueprint for routes
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Home page - redirects to login or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        prison_id = request.form.get('prison_id')
        password = request.form.get('password')

        user = User.query.get(prison_id)

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid prison ID or password')

    return render_template('login.html')

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
    current_step = Step.query.filter_by(step_number=current_user.current_step).first()
    return render_template('dashboard.html', current_step=current_step)

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

    # Redirect to first question
    first_question_id = questions[0].question_id
    return redirect(url_for('main.show_question', question_id=first_question_id))

@main.route('/question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def show_question(question_id):
    """Display single question"""
    question = Question.query.get(question_id)
    if not question:
        flash('Question not found.')
        return redirect(url_for('main.dashboard'))

    # Get question order from session
    question_order = session.get('question_order', [])
    current_index = session.get('current_question_index', 0)

    if request.method == 'POST':
        # Save the response
        if question.question_type == 'multiple_choice':
            selected_option_id = request.form.get('selected_option')
            response = Response(
                prison_id=current_user.prison_id,
                question_id=question_id,
                selected_option_id=selected_option_id
            )
        else:
            response_text = request.form.get('response_text')
            response = Response(
                prison_id=current_user.prison_id,
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

    # Calculate progress
    total_questions = len(question_order)
    progress = f"Question {current_index +1} of {total_questions}"

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
    # Advance user to next step
    if current_user.current_step < 12:
        current_user.current_step += 1
        db.session.commit()

    # Clear session data
    session.pop('question_order', None)
    session.pop('current_question_index', None)

    return render_template('assessment_complete.html')


