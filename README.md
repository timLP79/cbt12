# CBT 12-Step Assessment Application

A web-based cognitive behavioral therapy (CBT) assessment tool integrated with the 12-step recovery program, designed for use in correctional facilities.

## Project Overview

This application combines evidence-based Cognitive Behavioral Therapy principles with the 12-step recovery framework to provide structured assessments for individuals in prison treatment programs. Each of the 12 steps has an associated assessment consisting of multiple-choice and written response questions.

## Purpose

- **Academic Learning Project**: Built to learn full-stack web development with Python/Flask
- **Real-world Application**: Designed for an ex-colleague working in correctional treatment programs
- **Progressive Assessment**: Users complete steps sequentially, tracking their recovery journey

## Technology Stack

- **Backend**: Python 3.14, Flask
- **Database**: SQLite (development), upgradeable to PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Development Environment**: Distrobox (Fedora 43) + PyCharm Professional

## Project Structure
```
cbt-assessment/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── routes.py                # URL endpoints and authentication
│   └── templates/               # HTML templates
│       ├── base.html            # Base template with common layout
│       ├── login.html           # User login page
│       ├── dashboard.html       # User progress dashboard
│       ├── question.html        # Assessment question display
│       └── assessment_complete.html  # Completion confirmation
├── instance/
│   └── cbt_assessment.db        # SQLite database (not in git)
├── venv/                        # Virtual environment (not in git)
├── config.py                    # Configuration settings
├── init_db.py                   # Database initialization script
├── create_test_data.py          # Create test users and clinicians
├── add_sample_assessment.py     # Sample Step 1 assessment script
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── .gitignore
```

## Database Schema

### Core Tables

- **Users**: Participant information (prison_id, name, current_step, assigned clinician)
- **Clinicians**: Clinical staff who review assessments (with roles: clinician/supervisor/admin)
- **AssessmentAttempts**: Tracks each attempt at an assessment with review status
- **Steps**: The 12 recovery steps with descriptions
- **Assessments**: One assessment per step
- **Questions**: Individual questions (multiple choice or written)
- **MultipleChoiceOptions**: Answer choices for MC questions
- **Responses**: User answers linked to attempts, with clinician feedback support

### Workflow
The application implements a **clinician review workflow** where participants complete assessments, clinicians review submissions, and participants advance only after approval. This supports the Option D "Hybrid Approach" - flexible review with approval, revision, or supervisor referral options.

## Features

### ✅ Implemented

- **Database Foundation (Phase 1: Complete)**
  - 8 SQLAlchemy models with relationships:
    - Core: User, Clinician, AssessmentAttempt, Step, Assessment
    - Supporting: Question, MultipleChoiceOption, Response
  - Clinician review workflow support (attempt tracking, status management)
  - 12-step data seeding with titles and descriptions
  - Test data creation (2 participants, 2 clinicians)
  - Development and production configurations

- **Authentication & User Management**
  - Flask-Login based authentication
  - Prison ID and password login system
  - Session management
  - Protected routes with login requirement

- **Assessment System**
  - Question-by-question interface
  - Multiple choice questions with radio button selection
  - Written response questions with text area
  - Sequential question flow with progress tracking
  - Session-based question order persistence
  - Support for randomized or ordered questions
  - Automatic response recording to database

- **User Experience**
  - Dashboard showing current step and progress
  - Clear visual progress indicators during assessments
  - Assessment completion page
  - Automatic advancement to next step upon completion
  - Sequential step enforcement (must complete in order)

- **Development Tools**
  - Database initialization script (`init_db.py`)
  - Test user creation script (`create_test_user.py`)
  - Sample assessment generator for Step 1 (`add_sample_assessment.py`)

### 📋 To Be Implemented
- Admin dashboard for reviewing user responses
- Static CSS styling (currently using inline styles)
- Assessments for Steps 2-12 (only Step 1 has sample assessment)
- Progress visualization and analytics
- Data export functionality for treatment records
- Offline capability for institutional tablets
- Multi-therapist/administrator support

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip
- Git

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/YOUR-USERNAME/cbt-assessment.git
   cd cbt-assessment
```

2. **Create virtual environment**
```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Initialize the database**
```bash
python init_db.py
```

5. **Create test data** (users and clinicians for development)
```bash
python create_test_data.py
```
   This creates:
   - **Participants**: TEST001 (password123), TEST002 (password456)
   - **Clinicians**: CLIN001 (clinician123), CLIN002 (clinician456)

6. **Add sample assessment** (optional, for Step 1)
```bash
python add_sample_assessment.py
```
   This creates a 5-question sample assessment for Step 1.

7. **Run the application**
```bash
python run.py
```
   Navigate to `http://localhost:5000` and log in with the test credentials.

## Development Environment

This project is developed using:
- **Distrobox container** (Fedora 43) for isolated development
- **PyCharm Professional** with remote interpreter configuration
- **Git** for version control

## Privacy & Security Considerations

⚠️ **Important**: This application handles sensitive information:
- Personal identifiable information (names, prison IDs)
- Mental health and treatment data
- Vulnerable population data

**Security measures to implement:**
- Data encryption for sensitive fields
- Access control and authentication
- Institutional review board (IRB) approval before deployment
- Compliance with relevant privacy regulations

## Contributing

This is currently a personal learning project. Feedback and suggestions are welcome via issues.

## License

[To be determined]

## Contact

[Your contact information]

## Acknowledgments

- Designed in collaboration with correctional treatment professionals
- Built as an academic learning project
- Integrates evidence-based CBT with traditional 12-step methodology

---

**Project Status**: 🚧 Active Development - Phase 2 Complete

**Current Milestone**: **Phase 2 (Participant Flow) Complete!**
- ✅ Phase 1: Database schema with clinician review workflow
- ✅ Phase 2: Participant flow with attempt tracking and status display
  - AssessmentAttempt created on start, linked to all responses
  - Removed auto-advancement - users wait for clinician approval
  - Dynamic dashboard showing attempt status (Pending/Approved/Needs Revision)
  - Updated completion page with "Pending Review" messaging
  - Tested and verified working end-to-end

**Next Steps (Phase 3)**: Build clinician portal - login, dashboard, review interface, and approval actions. Then deploy to Render.com.

**Progress**: ~60% complete (participant side done, clinician side pending)