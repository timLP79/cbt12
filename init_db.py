from app import create_app, db
from app.models import Step

def init_database():
    """Initialize the database with tables and seed data"""
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created!")

        # Check if steps already exist
        if Step.query.first() is None:
            steps_data = [
                (1, "Step 1: Admission",
                 "We admitted we were powerless over our addiction - that our lives had become unmanageable"),
                (2, "Step 2: Hope", "Came to believe that a Power greater than ourselves could restore us to sanity"),
                (3, "Step 3: Surrender",
                 "Made a decision to turn our will and our lives over to the care of God as we understood Him"),
                (4, "Step 4: Soul Searching", "Made a searching and fearless moral inventory of ourselves"),
                (5, "Step 5: Integrity",
                 "Admitted to God, to ourselves, and to another human being the exact nature of our wrongs"),
                (6, "Step 6: Acceptance", "Were entirely ready to have God remove all these defects of character"),
                (7, "Step 7: Humility", "Humbly asked Him to remove our shortcomings"),
                (8, "Step 8: Willingness",
                 "Made a list of all persons we had harmed, and became willing to make amends to them all"),
                (9, "Step 9: Forgiveness",
                 "Made direct amends to such people wherever possible, except when to do so would injure them or others"),
                (10, "Step 10: Maintenance",
                 "Continued to take personal inventory and when we were wrong promptly admitted it"),
                (11, "Step 11: Making Contact",
                 "Sought through prayer and meditation to improve our conscious contact with God, improving our knowledge of His will"),
                (12, "Step 12: Service",
                 "Having had a spiritual awakening, we tried to carry this message to addicts, and to practice these principles in all our affairs"),
            ]

            for step_num, title, description in steps_data:
                step = Step(
                    step_number=step_num,
                    step_title=title,
                    step_description=description
                )
                db.session.add(step)

            db.session.commit()
            print("12 steps added to database!")
        else:
            print("Steps already exist in database")

if __name__ == '__main__':
    init_database()