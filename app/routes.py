from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models import User, Step, Assessment, Question, Response

# Create a blueprint for routes
main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Home page - redirects to login or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', method=['GET', 'POST'])
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