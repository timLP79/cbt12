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
    current_step = db.Column(db.Integer, default=1)

    # Relationship responses
    responses = db.relationship('Response', backref='user', lazy=True)

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
    prison_id = db.Column(db.String(50), db.ForeignKey('users.prison_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    response_text = db.Column(db.Text)  # For written responses
    selected_option_id = db.Column(db.Integer, db.ForeignKey('multiple_choice_options.option_id'))  # For MC
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)