from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from app import db
from app.models import User, Admin, AssessmentAttempt
from app.validators import (
    ValidationError,
    validate_state_id,
    validate_name,
    validate_password,
    validate_integer_id,
    validate_unique_state_id,
    validate_admin_id,
    validate_unique_email
)

manage = Blueprint('manage', __name__, url_prefix='/manage')


def supervisor_required(f):
    """Supervisor only"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Must be logged in as admin
        if not isinstance(current_user, Admin):
            abort(403)

        if current_user.role != 'supervisor':
            flash('This action requires supervisor privileges.')
            return redirect(url_for('admin.admin_dashboard'))

        return f(*args, **kwargs)

    return decorated_function


@manage.route('/users')
@login_required
@supervisor_required
def list_users():
    """List all users with search filters"""
    # Get query parameters from URL (?search=foo&step=2&admin=ADMIN001)
    search = request.args.get('search', '').strip()
    step_filter = request.args.get('step', '')
    admin_filter = request.args.get('admin', '')

    query = User.query

    if search:
        query = query.filter(
            db.or_(
                User.state_id.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )

    if step_filter:
        query = query.filter_by(current_step=int(step_filter))

    if admin_filter:
        query = query.filter_by(assigned_admin_id=admin_filter)

    users = query.order_by(User.last_name, User.first_name).all()

    # Admin list for filter dropdown
    all_admins = Admin.query.filter_by(is_active=True).order_by(Admin.last_name).all()

    return render_template('manage_users_list.html',
                           users=users,
                           all_admins=all_admins,
                           search=search,
                           step_filter=step_filter,
                           admin_filter=admin_filter)


@manage.route('/users/create', methods=['GET', 'POST'])
@login_required
@supervisor_required
def create_user():
    """Create new user"""
    if request.method == 'POST':
        try:
            state_id = validate_state_id(request.form.get('state_id'))
            validate_unique_state_id(state_id)
            first_name = validate_name(request.form.get('first_name'), 'First name')
            last_name = validate_name(request.form.get('last_name'), 'Last name')
            password = validate_password(request.form.get('password'))
            current_step = validate_integer_id(request.form.get('current_step', '1'))
            assigned_admin_id = request.form.get('assigned_admin_id') or None

            if current_step < 1 or current_step > 12:
                raise ValidationError("Step must be between 1 and 12")

            # Create new user object
            user = User(
                state_id=state_id,
                first_name=first_name,
                last_name=last_name,
                password_hash=generate_password_hash(password),
                current_step=current_step,
                assigned_admin_id=assigned_admin_id
            )

            db.session.add(user)
            db.session.commit()

            flash(f'User {state_id} created successfully!', 'success')
            return redirect(url_for('manage.list_users'))

        except ValidationError as e:
            flash(str(e), 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while creating the user.', 'error')

    # GET request - show empty form
    all_admins = Admin.query.filter_by(is_active=True).order_by(Admin.last_name).all()
    return render_template('manage_users_form.html',
                           admins=all_admins,
                           action='Create',
                           user=None)


@manage.route('/users/<state_id>/edit', methods=['GET', 'POST'])
@login_required
@supervisor_required
def edit_user(state_id):
    """Edit user details"""
    user = User.query.get_or_404(state_id)

    if request.method == 'POST':
        try:
            first_name = validate_name(request.form.get('first_name'), 'First name')
            last_name = validate_name(request.form.get('last_name'), 'Last name')
            current_step = validate_integer_id(request.form.get('current_step'))
            assigned_admin_id = request.form.get('assigned_admin_id') or None

            # Validate step range
            if current_step < 1 or current_step > 12:
                raise ValidationError("Step must be between 1 and 12")

            # Optional password change
            new_password = request.form.get('password', '').strip()
            if new_password:
                new_password = validate_password(new_password)
                user.password_hash = generate_password_hash(new_password)

            # Update user fields
            user.first_name = first_name
            user.last_name = last_name
            user.current_step = current_step
            user.assigned_admin_id = assigned_admin_id

            db.session.commit()

            flash(f'User {state_id} updated successfully!', 'success')
            return redirect(url_for('manage.list_users'))

        except ValidationError as e:
            flash(str(e), 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while updating the user.', 'error')

    # GET request - show empty form
    all_admins = Admin.query.filter_by(is_active=True).order_by(Admin.last_name).all()
    return render_template('manage_users_form.html',
                           admins=all_admins,
                           action='Edit',
                           user=user)


@manage.route('/users/<state_id>/deactivate', methods=['POST'])
@login_required
@supervisor_required
def deactivate_user(state_id):
    """Deactivate user (soft delete)"""
    user = User.query.get_or_404(state_id)

    user.is_active = False
    db.session.commit()

    flash(f'User {state_id} deactivated successfully.', 'success')
    return redirect(url_for('manage.list_users'))


@manage.route('/users/<state_id>/reactivate', methods=['POST'])
@login_required
@supervisor_required
def reactivate_user(state_id):
    """Reactivate a deactivated user"""
    user = User.query.get_or_404(state_id)

    user.is_active = True
    db.session.commit()

    flash(f'User {state_id} reactivated successfully.', 'success')
    return redirect(url_for('manage.list_users'))


# Manage admins
@manage.route('/admins')
@login_required
@supervisor_required
def list_admins():
    """List all admins with search filters"""
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '')

    query = Admin.query

    if search:
        query = query.filter(
            db.or_(
                Admin.admin_id.ilike(f'%{search}%'),
                Admin.first_name.ilike(f'%{search}%'),
                Admin.last_name.ilike(f'%{search}%'),
                Admin.email.ilike(f'%{search}%')
            )
        )

    if role_filter:
        query = query.filter_by(role=role_filter)

    admins = query.order_by(Admin.last_name, Admin.first_name).all()

    return render_template('manage_admins_list.html',
                           admins=admins,
                           search=search,
                           role_filter=role_filter
                           )


@manage.route('/admins/create', methods=['GET', 'POST'])
@login_required
@supervisor_required
def create_admin():
    """Create admin"""
    if request.method == 'POST':
        try:
            admin_id = validate_admin_id(request.form.get('admin_id'))
            if Admin.query.get(admin_id):
                raise ValidationError(f"Admin ID '{admin_id}' already exists.")

            first_name = validate_name(request.form.get('first_name'), 'First name')
            last_name = validate_name(request.form.get('last_name'), 'Last name')
            email = request.form.get('email', '').strip().lower()

            validate_unique_email(email)

            password = validate_password(request.form.get('password'))
            role = request.form.get('role', 'clinician')

            if role not in ['supervisor', 'clinician']:
                raise ValidationError("Invalid role selected.")

            new_admin = Admin(
                admin_id=admin_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=generate_password_hash(password),
                role=role
            )

            db.session.add(new_admin)
            db.session.commit()

            flash(f'Admin {admin_id} created successfully!', 'success')
            return redirect(url_for('manage.list_admins'))

        except ValidationError as e:
            flash(str(e), 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'An error occurred while creating the admin account.', 'error')

    return render_template('manage_admins_form.html',
                           action='Create',
                           admin=None)


@manage.route('/admins/<admin_id>/edit', methods=['GET', 'POST'])
@login_required
@supervisor_required
def edit_admin(admin_id):
    """Edit admin details"""
    admin = Admin.query.get_or_404(admin_id)
    if request.method == 'POST':
        try:
            first_name = validate_name(request.form.get('first_name'), 'First name')
            last_name = validate_name(request.form.get('last_name'), 'Last name')

            email = request.form.get('email', '').strip().lower()
            validate_unique_email(email, exclude_id=admin_id)

            role = request.form.get('role')
            if role not in ['clinician', 'supervisor']:
                raise ValidationError("Invalid role selected.")

            new_password = request.form.get('password', '').strip()
            if new_password:
                validate_password(new_password)
                admin.password_hash = generate_password_hash(new_password)

            admin.first_name = first_name
            admin.last_name = last_name
            admin.email = email
            admin.role = role

            db.session.commit()

            flash(f'Admin {admin_id} updated successfully!', 'success')
            return redirect(url_for('manage.list_admins'))

        except ValidationError as e:
            flash(str(e), 'error')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while updating the admin.', 'error')

    return render_template('manage_admins_form.html',
                           action='Edit',
                           admin=admin)


@manage.route('/admins/<admin_id>/deactivate', methods=['POST'])
@login_required
@supervisor_required
def deactivate_admin(admin_id):
    """Deactivate admin (soft delete)"""
    # Prevent self-deactivation
    if admin_id == current_user.admin_id:
        flash("You cannot deactivate your own account.", "error")
        return redirect(url_for('manage.list_admins'))

    admin=Admin.query.get_or_404(admin_id)
    admin.is_active = False
    db.session.commit()

    flash(f'Admin {admin_id} deactivated successfully.', 'success')
    return redirect(url_for('manage.list_admins'))


@manage.route('/admins/<admin_id>/reactivate', methods=['POST'])
@login_required
@supervisor_required
def reactivate_admin(admin_id):
    """Reactivate a deactivated admin"""
    admin = Admin.query.get_or_404(admin_id)

    admin.is_active = True
    db.session.commit()

    flash(f'Admin {admin_id} reactivated successfully.', 'success')
    return redirect(url_for('manage.list_admins'))


@manage.route('/users/<state_id>')
@login_required
@supervisor_required
def user_profile(state_id):
    """View detailed user profile and history"""
    user = User.query.get_or_404(state_id)

    attempts = AssessmentAttempt.query.filter_by(state_id=state_id).order_by(AssessmentAttempt.submitted_at.desc()).all()

    return render_template('user_profile.html', user=user, attempts=attempts)
