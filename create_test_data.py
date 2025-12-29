from app import create_app, db
from app.models import User, Admin
from werkzeug.security import generate_password_hash


def create_test_data():
    """Create test users and admins for development"""
    app = create_app()

    with app.app_context():
        user1 = User(
            state_id='TEST001',
            first_name='David',
            last_name='Fisher',
            password_hash=generate_password_hash('password123'),
            current_step=1
        )

        user2 = User(
            state_id='TEST002',
            first_name='John',
            last_name='Doe',
            password_hash=generate_password_hash('password456'),
            current_step=1
        )

        admin1 = Admin(
            admin_id='ADMIN001',
            first_name='Tim',
            last_name='Palacios',
            email='timlpalacios@gmail.com',
            password_hash=generate_password_hash('admin123'),
            role='supervisor'
        )

        admin2 = Admin(
            admin_id='ADMIN002',
            first_name='Sandra',
            last_name='Riggs',
            email='test@email.com',
            password_hash=generate_password_hash('admin456'),
            role='clinician'
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(admin1)
        db.session.add(admin2)
        db.session.commit()

        print("Created test users:")
        print(f" - {user1.state_id}: {user1.first_name} {user1.last_name}")
        print(f" - {user2.state_id}: {user2.first_name} {user2.last_name}")
        print()
        print("Created test admins:")
        print(f" - {admin1.admin_id}: {admin1.first_name} {admin1.last_name}")
        print(f" - {admin2.admin_id}: {admin2.first_name} {admin2.last_name}")


if __name__ == '__main__':
    create_test_data()
