from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import ExceptionContext
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from app import db
from app.models import User, Admin
from app.validators import (
    ValidationError,
    validate_state_id,
    validate_name,
    validate_password,
    validate_integer_id,
    validate_unique_state_id
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


