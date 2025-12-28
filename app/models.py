from sqlalchemy.orm import backref

from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(prison_id):
    return User.query.get(prison_id)

class User(db.Model, UserMixin):
    """Participant taking assessment"""
    __tablename__ = 'users'

    prison_id = db.Column(db.String(50), primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    date_enrolled = db.Column(db.DateTime, default=datetime.utcnow)

    # Program tracking
    current_step = db.Column(db.Integer, default=1)
    assigned_clinician_id = db.Column(db.String(50), db.ForeignKey('clinicians.clinician_id'), nullable=True)

    # Relationships
    assigned_clinician = db.relationship('Clinician', backref='assigned_participants', lazy=True)

    def get_id(self):
        return self.prison_id


class Step(db.Model):
    """The 12 steps"""
    __tablename__ = 'steps'

    step_id = db.Column(db.Integer, primary_key=True)
    step_number = db.Column(db.Integer, unique=True, nullable=False)
    step_title = db.Column(db.String(500), nullable=False)
    step_description = db.Column(db.Text)

    # Relationship to assessments
    assessments = db.relationship('Assessment', backref='step', lazy=True)


class Assessment(db.Model):
    """One assessment per step"""
    __tablename__ = 'assessments'

    assessment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    step_id = db.Column(db.Integer, db.ForeignKey('steps.step_id'), nullable=False)
    assessment_title = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text)
    randomize_questions = db.Column(db.Boolean, default=False)

    # Relationship to questions
    questions = db.relationship('Question', backref='assessment', lazy=True)


class AssessmentAttempt(db.Model):
    """Tracks each attempt at an assessment and its review status"""
    __tablename__ = 'assessment_attempts'

    attempt_id = db.Column(db.Integer, primary_key=True)
    prison_id = db.Column(db.String(50), db.ForeignKey('users.prison_id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.assessment_id'), nullable=False)
    attempt_number = db.Column(db.Integer, default=1, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='in_progress', nullable=False)
    reviewed_by = db.Column(db.String(50), db.ForeignKey('clinicians.clinician_id'),nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    clinician_notes = db.Column(db.Text, nullable=True)
    score = db.Column(db.Integer, nullable=True)

    # Relationships
    user = db.relationship('User', backref='attempts', lazy=True)
    assessment = db.relationship('Assessment', backref='attempts', lazy=True)
    responses = db.relationship('Response', backref='attempt', lazy=True)

class Clinician(db.Model, UserMixin):
    """Clinical staff who review assessments"""
    __tablename__ = 'clinicians'

    clinician_id = db.Column(db.String(50), primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='clinician', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reviewed_attempts = db.relationship('AssessmentAttempt', backref='reviewer', lazy=True)

    def get_id(self):
        return self.clinician_id


class Question(db.Model):
    """Questions within an assessment"""
    __tablename__ = 'questions'

    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.assessment_id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # 'multiple_choice' or 'written'
    question_order = db.Column(db.Integer, nullable=False)

    # Relationships
    options = db.relationship('MultipleChoiceOption', backref='question', lazy=True)
    responses = db.relationship('Response', backref='question', lazy=True)


class MultipleChoiceOption(db.Model):
    """Answer options for multiple choice questions"""
    __tablename__ = 'multiple_choice_options'

    option_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    option_text = db.Column(db.String(500), nullable=False)
    option_value = db.Column(db.Integer)  # For scoring if needed


class Response(db.Model):
    """User responses to questions"""
    __tablename__ = 'responses'

    response_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('assessment_attempts.attempt_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    response_text = db.Column(db.Text)  # For written responses
    selected_option_id = db.Column(db.Integer, db.ForeignKey('multiple_choice_options.option_id'))  # For MC
    clinician_comment = db.Column(db.Text, nullable=True)
    needs_revision = db.Column(db.Boolean, default=False, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)