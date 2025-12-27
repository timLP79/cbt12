from app import create_app, db
from app.models import Assessment, Question, MultipleChoiceOption

def add_sample_assessment():
    """Add a sample assessment for Step 1"""
    app = create_app()

    with app.app_context():
        # Check if assessment already exists
        existing = Assessment.query.filter_by(step_id=1).first()
        if existing:
            print("Assessment for Step 1 already exists")
            return

        #Create assessment for step 1
        assessment = Assessment(
            step_id=1,
            assessment_title="Step 1: Powerless and Unmanageability Assessment",
            instructions="Please answer the following questions honestly. This assessment will help evaluate your understanding of Step 1.",
            randomize_questions=False
        )
        db.session.add(assessment)
        db.session.flush() # Get assessment_id

        # Question 1 - Multiple choice
        q1 = Question(
            assessment_id=assessment.assessment_id,
            question_text="How often do you feel that your addiction controls your life rather than you controlling it?",
            question_type="multiple_choice",
            question_order=1
        )
        db.session.add(q1)
        db.session.flush()

        # Options for Question 1
        options_q1 = [
            ("Never", 1),
            ("Rarely", 2),
            ("Sometimes", 3),
            ("Often", 4),
            ("Always", 5)
        ]

        for option_text, value in options_q1:
            option = MultipleChoiceOption(
                question_id=q1.question_id,
                option_text=option_text,
                option_value=value
            )
            db.session.add(option)

        # Question 2 - Multiple Choice
        q2 = Question(
            assessment_id=assessment.assessment_id,
            question_text="To what extent has your addiction made your life unmanageable?",
            question_type="multiple_choice",
            question_order=2
        )
        db.session.add(q2)
        db.session.flush()

        # Options for Question 2
        options_q2 = [
            ("Not at all", 1),
            ("Slightly", 2),
            ("Moderately", 3),
            ("Significantly", 4),
            ("Completely", 5)
        ]

        for option_text, value in options_q2:
            option = MultipleChoiceOption(
                question_id=q2.question_id,
                option_text=option_text,
                option_value=value
            )
            db.session.add(option)

        # Question 3 - Written Response
        q3 = Question(
            assessment_id=assessment.assessment_id,
            question_text="Describe a specific situation where you felt powerless over your addiction.",
            question_type="written",
            question_order=3
        )
        db.session.add(q3)

        # Question 4 - Multiple Choice
        q4 = Question(
            assessment_id=assessment.assessment_id,
            question_text="Do you believe that admitting powerlessness is a sign of strength or weakness?",
            question_type="multiple_choice",
            question_order=4
        )
        db.session.add(q4)
        db.session.flush()

        # Options for Question 4
        options_q4 = [
            ("Definitely a weakness", 1),
            ("More of a weakness", 2),
            ("Neither strength nor weakness", 3),
            ("More of a strength", 4),
            ("Definitely a strength", 5)
        ]

        for option_text, value in options_q4:
            option = MultipleChoiceOption(
                question_id=q4.question_id,
                option_text=option_text,
                option_value=value
            )
            db.session.add(option)

        # Question 5 - Written Response
        q5 = Question(
            assessment_id=assessment.assessment_id,
            question_text="What does 'unmanageable life' mean to you personally?",
            question_type="written",
            question_order=5
        )
        db.session.add(q5)

        db.session.commit()
        print("Sample assessment for Step 1 created successfully!")
        print("- 5 questions total")
        print("- 3 multiple choice questions")
        print("- 2 written response questions")

if __name__ == '__main__':
    add_sample_assessment()