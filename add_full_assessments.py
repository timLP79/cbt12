from app import create_app, db
from app.models import Assessment, Question, MultipleChoiceOption


def add_full_assessments():
    """Add assessments for Steps 2-12"""
    app = create_app()

    with app.app_context():
        # Define content for Steps 1-12
        assessments_data = [
            # Step 1: Powerlessness (Added from tmp.py)
            {
                "step_id": 1,
                "title": "Step 1: Powerless and Unmanageability Assessment",
                "instructions": "Please answer the following questions honestly. This assessment will help evaluate your understanding of Step 1.",
                "questions": [
                    {
                        "text": "How often do you feel that your addiction controls your life rather than you controlling it?",
                        "type": "multiple_choice",
                        "options": [("Never", 1), ("Rarely", 2), ("Sometimes", 3), ("Often", 4), ("Always", 5)]
                    },
                    {
                        "text": "To what extent has your addiction made your life unmanageable?",
                        "type": "multiple_choice",
                        "options": [("Not at all", 1), ("Slightly", 2), ("Moderately", 3), ("Significantly", 4), ("Completely", 5)]
                    },
                    {
                        "text": "Describe a specific situation where you felt powerless over your addiction.",
                        "type": "written"
                    },
                    {
                        "text": "Do you believe that admitting powerlessness is a sign of strength or weakness?",
                        "type": "multiple_choice",
                        "options": [("Definitely a weakness", 1), ("More of a weakness", 2), ("Neither strength nor weakness", 3), ("More of a strength", 4), ("Definitely a strength", 5)]
                    },
                    {
                        "text": "What does 'unmanageable life' mean to you personally?",
                        "type": "written"
                    }
                ]
            },
            # Step 2: Hope
            {
                "step_id": 2,
                "title": "Step 2: Restored to Sanity",
                "instructions": "Reflect on your beliefs about recovery and a power greater than yourself.",
                "questions": [
                    {
                        "text": "Do you believe it is possible for you to recover from addiction?",
                        "type": "multiple_choice",
                        "options": [("Yes, absolutely", 5), ("I hope so", 4), ("I'm unsure", 3), ("Probably not", 2), ("No", 1)]
                    },
                    {
                        "text": "What does 'sanity' look like to you compared to your active addiction?",
                        "type": "written"
                    },
                    {
                        "text": "Are you willing to believe in a power greater than yourself (even if it's just the group or a concept)?",
                        "type": "multiple_choice",
                        "options": [("Yes, fully", 5), ("I am willing to try", 4), ("I have doubts", 3), ("No, I struggle with this", 1)]
                    },
                    {
                        "text": "Have you seen evidence of recovery in others that gives you hope?",
                        "type": "multiple_choice",
                        "options": [("Yes, often", 5), ("Sometimes", 3), ("No, never", 1)]
                    },
                    {
                        "text": "Describe one specific insanity (repeated behavior expecting different results) you want to be restored from.",
                        "type": "written"
                    }
                ]
            },
            # Step 3: Surrender
            {
                "step_id": 3,
                "title": "Step 3: Turning It Over",
                "instructions": "This step is about decision making and letting go of control.",
                "questions": [
                    {
                        "text": "What fears do you have about turning your will over to a higher power?",
                        "type": "written"
                    },
                    {
                        "text": "How often do you try to control outcomes that are beyond your power?",
                        "type": "multiple_choice",
                        "options": [("Constantly", 1), ("Often", 2), ("Sometimes", 3), ("Rarely", 4), ("Never", 5)]
                    },
                    {
                        "text": "Are you ready to stop fighting and start accepting help?",
                        "type": "multiple_choice",
                        "options": [("Yes, I surrender", 5), ("I want to", 4), ("I'm scared", 3), ("No", 1)]
                    },
                    {
                        "text": "What areas of your life are you still holding back from turning over?",
                        "type": "written"
                    },
                    {
                        "text": "Does 'turning it over' mean doing nothing?",
                        "type": "multiple_choice",
                        "options": [("No, it means doing the footwork and leaving the results", 5), ("Yes, sitting back", 1), ("I don't know", 3)]
                    }
                ]
            },
            # Step 4: Inventory
            {
                "step_id": 4,
                "title": "Step 4: Moral Inventory",
                "instructions": "Be searching and fearless. Honesty is critical here.",
                "questions": [
                    {
                        "text": "List three major resentments you are currently holding onto.",
                        "type": "written"
                    },
                    {
                        "text": "What is a primary fear that has driven your behavior?",
                        "type": "written"
                    },
                    {
                        "text": "How do you rate your current level of honesty with yourself?",
                        "type": "multiple_choice",
                        "options": [("Brutally honest", 5), ("Mostly honest", 4), ("Somewhat honest", 3), ("Avoidant", 2), ("Dishonest", 1)]
                    },
                    {
                        "text": "Identify a pattern of sexual conduct that has caused harm to yourself or others.",
                        "type": "written"
                    },
                    {
                        "text": "Are you willing to look at your own part in these situations?",
                        "type": "multiple_choice",
                        "options": [("Yes, fully", 5), ("Reluctantly", 3), ("No, it's their fault", 1)]
                    }
                ]
            },
            # Step 5: Integrity
            {
                "step_id": 5,
                "title": "Step 5: Admitting Wrongs",
                "instructions": "This step requires sharing your inventory with another person.",
                "questions": [
                    {
                        "text": "How do you feel about sharing your secrets with another person?",
                        "type": "multiple_choice",
                        "options": [("Relieved", 5), ("Ready", 4), ("Nervous but willing", 3), ("Terrified", 2), ("Unwilling", 1)]
                    },
                    {
                        "text": "What is the value of admitting your wrongs to another human being?",
                        "type": "written"
                    },
                    {
                        "text": "Have you chosen someone trustworthy to hear your step 5?",
                        "type": "multiple_choice",
                        "options": [("Yes", 5), ("Thinking about it", 3), ("No", 1)]
                    },
                    {
                        "text": "What specific secret are you most afraid to tell?",
                        "type": "written"
                    },
                    {
                        "text": "Do you believe this step is necessary for long-term sobriety?",
                        "type": "multiple_choice",
                        "options": [("Yes", 5), ("Maybe", 3), ("No", 1)]
                    }
                ]
            },
            # Step 6: Acceptance
            {
                "step_id": 6,
                "title": "Step 6: Ready for Change",
                "instructions": "Focus on your willingness to let go of character defects.",
                "questions": [
                    {
                        "text": "List one character defect you are entirely ready to have removed.",
                        "type": "written"
                    },
                    {
                        "text": "Are you holding onto any defects because they feel comfortable or safe?",
                        "type": "multiple_choice",
                        "options": [("No, I want them all gone", 5), ("Maybe a few", 3), ("Yes, I'm afraid to change", 1)]
                    },
                    {
                        "text": "How does this defect (the one you listed above) negatively impact your life?",
                        "type": "written"
                    },
                    {
                        "text": "Do you believe God/Higher Power can remove these defects?",
                        "type": "multiple_choice",
                        "options": [("Yes", 5), ("I hope so", 3), ("No", 1)]
                    },
                    {
                        "text": "Are you willing to act differently if the defect is removed?",
                        "type": "multiple_choice",
                        "options": [("Yes", 5), ("I'll try", 3), ("No", 1)]
                    }
                ]
            },
            # Step 7: Humility
            {
                "step_id": 7,
                "title": "Step 7: Asking for Removal",
                "instructions": "Humility is seeing ourselves in true perspective.",
                "questions": [
                    {
                        "text": "Define 'humility' in your own words.",
                        "type": "written"
                    },
                    {
                        "text": "How does asking for help differ from demanding change?",
                        "type": "written"
                    },
                    {
                        "text": "How often do you practice asking for help in your daily life?",
                        "type": "multiple_choice",
                        "options": [("Daily", 5), ("Sometimes", 3), ("Rarely", 1)]
                    },
                    {
                        "text": "What specific shortcoming causes you the most trouble today?",
                        "type": "written"
                    },
                    {
                        "text": "Do you feel a sense of peace when asking humbly?",
                        "type": "multiple_choice",
                        "options": [("Yes", 5), ("Sometimes", 3), ("No", 1)]
                    }
                ]
            },
            # Step 8: Willingness
            {
                "step_id": 8,
                "title": "Step 8: List of Amends",
                "instructions": "Make a list of all persons you have harmed.",
                "questions": [
                    {
                        "text": "Do you have a physical list of people you have harmed?",
                        "type": "multiple_choice",
                        "options": [("Yes, a complete list", 5), ("I have started one", 3), ("No, not yet", 1)]
                    },
                    {
                        "text": "Are you willing to make amends to everyone on that list?",
                        "type": "multiple_choice",
                        "options": [("Yes, everyone", 5), ("Most of them", 4), ("Only some", 2), ("No", 1)]
                    },
                    {
                        "text": "Who is the hardest person on your list to face?",
                        "type": "written"
                    },
                    {
                        "text": "Why is it important to focus on 'your side of the street'?",
                        "type": "written"
                    },
                    {
                        "text": "Have you included yourself on the list of people harmed?",
                        "type": "multiple_choice",
                        "options": [("Yes", 5), ("No", 1)]
                    }
                ]
            },
            # Step 9: Forgiveness
            {
                "step_id": 9,
                "title": "Step 9: Making Amends",
                "instructions": "Direct amends wherever possible.",
                "questions": [
                    {
                        "text": "What is the difference between an apology and an amend?",
                        "type": "written"
                    },
                    {
                        "text": "Have you considered how an amend might injure someone else?",
                        "type": "multiple_choice",
                        "options": [("Yes, carefully", 5), ("Somewhat", 3), ("No, I haven't thought about it", 1)]
                    },
                    {
                        "text": "Describe a specific plan for one of your amends.",
                        "type": "written"
                    },
                    {
                        "text": "Are you prepared for the other person to not accept your amend?",
                        "type": "multiple_choice",
                        "options": [("Yes, I can handle it", 5), ("I'm worried about it", 3), ("No, I expect forgiveness", 1)]
                    },
                    {
                        "text": "How will making these amends help your recovery?",
                        "type": "written"
                    }
                ]
            },
            # Step 10: Maintenance
            {
                "step_id": 10,
                "title": "Step 10: Daily Inventory",
                "instructions": "Continue to watch for selfishness, dishonesty, resentment, and fear.",
                "questions": [
                    {
                        "text": "How often do you plan to take personal inventory?",
                        "type": "multiple_choice",
                        "options": [("Daily", 5), ("Weekly", 4), ("Only when in trouble", 2), ("Rarely", 1)]
                    },
                    {
                        "text": "When you are wrong, do you promptly admit it?",
                        "type": "multiple_choice",
                        "options": [("Always", 5), ("Usually", 4), ("Sometimes", 3), ("Rarely", 2), ("Never", 1)]
                    },
                    {
                        "text": "What tool will you use to keep track of your daily inventory (journal, app, sponsor)?",
                        "type": "written"
                    },
                    {
                        "text": "Describe a recent situation where you had to admit you were wrong.",
                        "type": "written"
                    },
                    {
                        "text": "Is this step becoming a habit for you?",
                        "type": "multiple_choice",
                        "options": [("Yes", 5), ("Starting to", 3), ("No", 1)]
                    }
                ]
            },
            # Step 11: Making Contact
            {
                "step_id": 11,
                "title": "Step 11: Prayer and Meditation",
                "instructions": "Improve your conscious contact.",
                "questions": [
                    {
                        "text": "Describe your current practice of prayer or meditation.",
                        "type": "written"
                    },
                    {
                        "text": "What does 'conscious contact' mean to you?",
                        "type": "written"
                    },
                    {
                        "text": "Do you set aside specific time each morning for this step?",
                        "type": "multiple_choice",
                        "options": [("Yes, every morning", 5), ("Most mornings", 4), ("Sometimes", 3), ("No", 1)]
                    },
                    {
                        "text": "What does 'God's will for us' look like in your life today?",
                        "type": "written"
                    },
                    {
                        "text": "Do you pause when agitated or doubtful?",
                        "type": "multiple_choice",
                        "options": [("Yes, usually", 5), ("Sometimes", 3), ("No, I react instantly", 1)]
                    }
                ]
            },
            # Step 12: Service
            {
                "step_id": 12,
                "title": "Step 12: Carrying the Message",
                "instructions": "Practice these principles in all your affairs.",
                "questions": [
                    {
                        "text": "How can you be of service to others in recovery?",
                        "type": "written"
                    },
                    {
                        "text": "Do you feel you have had a spiritual awakening as the result of these steps?",
                        "type": "multiple_choice",
                        "options": [("Yes, definitely", 5), ("A slow change", 4), ("I'm getting there", 3), ("Not yet", 1)]
                    },
                    {
                        "text": "Are you ready to sponsor or help another person?",
                        "type": "multiple_choice",
                        "options": [("Yes", 5), ("Maybe later", 3), ("No", 1)]
                    },
                    {
                        "text": "What does 'practicing these principles in all our affairs' mean to you?",
                        "type": "written"
                    },
                    {
                        "text": "Are you committed to continuing this way of life?",
                        "type": "multiple_choice",
                        "options": [("Yes, one day at a time", 5), ("I hope so", 3), ("I don't know", 1)]
                    }
                ]
            }
        ]

        print("Starting to seed assessments for Steps 1-12...")
        
        for data in assessments_data:
            # Check if exists
            existing = Assessment.query.filter_by(step_id=data['step_id']).first()
            if existing:
                print(f"Skipping Step {data['step_id']} - Assessment already exists.")
                continue

            # Create Assessment
            assessment = Assessment(
                step_id=data['step_id'],
                assessment_title=data['title'],
                instructions=data['instructions'],
                randomize_questions=False
            )
            db.session.add(assessment)
            db.session.flush()

            # Add Questions
            for index, q_data in enumerate(data['questions']):
                question = Question(
                    assessment_id=assessment.assessment_id,
                    question_text=q_data['text'],
                    question_type=q_data['type'],
                    question_order=index + 1
                )
                db.session.add(question)
                db.session.flush()

                # Add Options if Multiple Choice
                if q_data['type'] == 'multiple_choice':
                    for opt_text, opt_val in q_data['options']:
                        option = MultipleChoiceOption(
                            question_id=question.question_id,
                            option_text=opt_text,
                            option_value=opt_val
                        )
                        db.session.add(option)
            
            print(f"Created Assessment for Step {data['step_id']}")
        
        db.session.commit()
        print("Done! All 12 steps now have assessments with 5 questions each.")

if __name__ == '__main__':
    add_full_assessments()
