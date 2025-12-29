from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash


def create_test_user():
    """Create a test user for development"""
    app = create_app()

    with app.app_context():
        # Check if user already exists
        existing_user = User.query.get('TEST001')
        if existing_user:
            print("Test user already exists!")
            return

        # Create test user
        test_user = User(
            prison_id='TEST001',
            first_name='John',
            last_name='Doe',
            password_hash=generate_password_hash('password123'),
            current_step=1
        )

        db.session.add(test_user)
        db.session.commit()

        print("Test user created successfully!")
        print("Prison ID: TEST001")
        print("Password: password123")
        print("Current Step: 1")


if __name__ == '__main__':
    create_test_user()
