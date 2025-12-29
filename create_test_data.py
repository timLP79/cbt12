from app import create_app, db
from app.models import User, Admin
from werkzeug.security import generate_password_hash


def create_test_data():
    """Create test users and clinicians for development"""
    app = create_app()

    with app.app_context():
        user1 = User(
            prison_id='TEST001',
            first_name='David',
            last_name='Fisher',
            password_hash=generate_password_hash('password123'),
            current_step=1
        )

        user2 = User(
            prison_id='TEST002',
            first_name='John',
            last_name='Doe',
            password_hash=generate_password_hash('password456'),
            current_step=1
        )

        clinician1 = Admin(
            clinician_id='CLIN001',
            first_name='Tim',
            last_name='Palacios',
            email='timlpalacios@gmail.com',
            password_hash=generate_password_hash('clinician123'),
            role='supervisor'
        )

        clinician2 = Admin(
            clinician_id='CLIN002',
            first_name='Sandra',
            last_name='Riggs',
            email='test@email.com',
            password_hash=generate_password_hash('clinician456'),
            role='clinician'
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.add(clinician1)
        db.session.add(clinician2)
        db.session.commit()

        print("Created test users:")
        print(f" - {user1.prison_id}: {user1.first_name} {user1.last_name}")
        print(f" - {user2.prison_id}: {user2.first_name} {user2.last_name}")
        print()
        print("Created test clinicians:")
        print(f" - {clinician1.clinician_id}: {clinician1.first_name} {clinician1.last_name}")
        print(f" - {clinician2.clinician_id}: {clinician2.first_name} {clinician2.last_name}")


if __name__ == '__main__':
    create_test_data()
