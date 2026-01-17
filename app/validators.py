"""
Input validation functions for the CBT Application
"""
import re


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_decision(decision):
    """
    Validate admin review decision.
    Must be 'approve' or 'needs_revision'.
    """
    if not decision:
        raise ValidationError("A review decision is required.")

    allowed_decisions = ['approve', 'needs_revision']

    if decision not in allowed_decisions:
        raise ValidationError(f"Invalid decision. Must be one of: {', '.join(allowed_decisions)}")

    return decision


def validate_password(password):
    """
    validate password format
    """
    if not password:
        raise ValidationError("Password is required.")

    if len(password) < 4:
        raise ValidationError("Password must be at least 4 characters.")
    elif len(password) > 128:
        raise ValidationError("Password is too long (max 128 characters.)")

    # Check for uppercase
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")

    # Check for special character
    if not re.search(r'[^A-Za-z0-9]', password):
        raise ValidationError("Password must contain at least one special character.")

    return password


def validate_text_response(text, field_name="Response", max_length=5000):
    """
    Validate free-text responses.
    Checks for reasonable length and dangerous content
    """
    if text is None:
        return ""

    text = text.strip()

    if not text:
        return ""

    if len(text) > max_length:
        raise ValidationError(f"Text is too long (max {max_length} characters).")

    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'onerror\s*=',
        r'onload\s*=',
        r'onclick\s*='
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValidationError(f"{field_name} contains potentially dangerous content.")

    return text


def validate_state_id(state_id):
    """
    Validate State ID format.
    Must start with 2 uppercase letters, followed by 4 to 10 digits.
    """
    if not state_id:
        raise ValidationError("State ID is required.")

    state_id = state_id.strip().upper()  # Convert to uppercase for consistent validation

    # The pattern now explicitly enforces:
    # ^     - start of the string
    # [A-Z]{2} - exactly two uppercase letters (the state code)
    # \d{4,10} - exactly 4 to 10 digits (the unique ID part)
    # $     - end of the string
    pattern = r'^[A-Z]{2}\d{4,10}$'

    if re.match(pattern, state_id) is None:
        # Provide a clear, actionable error message
        raise ValidationError(
            "Invalid State ID format. Must start with 2 uppercase letters followed by 4 to 10 digits (e.g., TX123456)."
        )

    return state_id


def validate_admin_id(admin_id):
    """
    Validate Admin ID format
    """
    if not admin_id:
        raise ValidationError("Admin ID is required.")

    admin_id = admin_id.strip()

    if len(admin_id) < 4:
        raise ValidationError("Admin ID must be at least 4 characters.")
    elif len(admin_id) > 20:
        raise ValidationError("Admin ID is too long (max 20 characters.)")

    pattern = r'^[A-Za-z0-9-]+$'

    if re.match(pattern, admin_id) is None:
        raise ValidationError("Admin ID can only contain letters, numbers and hyphens.")

    return admin_id


def validate_integer_id(value, field_name="ID"):
    """
    Validate that a value is a valid integer ID.
    Returns the integer value.
    """
    if value is None:
        raise ValidationError(f"{field_name} is required.")

    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number.")

    if int_value < 1:
        raise ValidationError(f"{field_name} must be a positive number.")

    return int_value


def validate_name(name, field_name="Name"):
    """
    Validate first/last name fields
    - Strip whitepace
    - Min 1 char, max 100 chars
    - Only letters, spaces, hyphens, apostrophes
    """
    if not name:
        raise ValidationError(f"{field_name} is required")

    name = name.strip()

    if len(name) < 1 or len(name) > 100:
        raise ValidationError(f"{field_name} must be between 1 and 100 characters")

    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        raise ValidationError(f"{field_name} can only contain letters, spaces, hyphens, and apostrophes")

    return name


def validate_unique_state_id(state_id, exclude_id=None):
    """
    Check if state_id already exists in the database

    Args:
        state_id: The State ID to check
        exclude_id: Optional state_id to exclude (for editing existing users)
    """
    from app.models import User

    query = User.query.filter_by(state_id=state_id)

    if exclude_id:
        query = query.filter(User.state_id != exclude_id)

    if query.first():
        raise ValidationError(f"State ID '{state_id}' already exists")


def validate_unique_email(email, exclude_id=None):
    """
    Check if email already exists in database

    Args:
        email: The email to check
        exclude_id: Optional admin_id to exclude (for editing existing admin)
    """
    from app.models import Admin

    query = Admin.query.filter_by(email=email)

    if exclude_id:
        query = query.filter(Admin.admin_id != exclude_id)

    if query.first():
        raise ValidationError(f"Email '{email}' already exists")
