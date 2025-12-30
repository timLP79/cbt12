# CBT 12-Step Assessment Application

A web-based cognitive behavioral therapy (CBT) assessment tool integrated with the 12-step recovery program, designed for use in treatment facilities and correctional programs.

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
- **Security**: Flask-WTF (CSRF), Flask-Limiter (Rate Limiting)
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

- **Users**: Participant information (state_id, name, current_step, assigned admin)
- **Admins**: Administrative staff who review assessments (with roles: clinician/supervisor)
- **AssessmentAttempts**: Tracks each attempt at an assessment with review status
- **Steps**: The 12 recovery steps with descriptions
- **Assessments**: One assessment per step
- **Questions**: Individual questions (multiple choice or written)
- **MultipleChoiceOptions**: Answer choices for MC questions
- **Responses**: User answers linked to attempts, with clinician feedback support

### Workflow
The application implements a **clinician review workflow** where participants complete assessments, administrative staff (clinicians/supervisors) review submissions, and participants advance only after approval. This supports a flexible review approach with approval, revision, or supervisor referral options.

## Features

### ✅ Implemented

- **Database Foundation (Phase 1: Complete)**
  - 8 SQLAlchemy models with relationships:
    - Core: User, Admin, AssessmentAttempt, Step, Assessment
    - Supporting: Question, MultipleChoiceOption, Response
  - Admin review workflow support (attempt tracking, status management)
  - 12-step data seeding with titles and descriptions
  - Test data creation (2 participants, 2 admins)
  - Development and production configurations

- **Authentication & User Management (Dual Login System)**
  - Flask-Login based authentication with role-based access
  - Participant login (State ID and password)
  - Admin login (Admin ID and password)
  - Session management with user type tracking
  - Protected routes with login requirement

- **Assessment System**
  - Question-by-question interface
  - Multiple choice questions with radio button selection
  - Written response questions with text area
  - Sequential question flow with progress tracking
  - Session-based question order persistence
  - Support for randomized or ordered questions
  - Automatic response recording to database

- **Participant Experience (Phase 2: Complete)**
  - Dashboard showing current step and progress
  - Dynamic status display (Pending Review, Approved, Needs Revision)
  - Clear visual progress indicators during assessments
  - Assessment completion page with pending review messaging
  - Sequential step enforcement (must complete in order)
  - No auto-advancement - requires admin approval

- **Admin Portal (Phase 3: Complete)**
  - Admin dashboard showing pending assessments
  - Review interface displaying all participant responses
  - Approval/revision workflow with feedback notes
  - Participant advancement upon approval
  - Separate admin login portal

- **Development Tools**
  - Database initialization script (`init_db.py`)
  - Test user creation script (`create_test_data.py`)
  - Sample assessment generator for Step 1 (`add_sample_assessment.py`)

### 📋 To Be Implemented
- **Performance optimization** (database indexes, N+1 query fixes, transaction rollback)
- Static CSS styling (currently using inline styles)
- Assessments for Steps 2-12 (only Step 1 has sample assessment)
- Progress visualization and analytics
- Data export functionality for treatment records
- Custom error pages (404, 403, 500)
- Offline capability for institutional tablets

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

5. **Create test data** (users and admins for development)
```bash
python create_test_data.py
```
   This creates:
   - **Participants**: TEST001 (password123), TEST002 (password456)
   - **Admins**: ADMIN001 (admin123), ADMIN002 (admin456)

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

**Project Status**: 🚧 Active Development - Phase 4 Security Hardening ~90% Complete

**Current Milestone**: **Phase 4 (Security Hardening) Nearly Complete!**
- ✅ Phase 1: Database schema with admin review workflow
- ✅ Phase 2: Participant flow with attempt tracking and status display
- ✅ Phase 3: Admin portal with review and approval workflow
- ✅ Major Refactoring (Dec 2025): Clinician → Admin, prison_id → state_id
- ✅ Phase 4 Security (Critical & High Priority - Dec 2025):
  - **CSRF Protection** - Flask-WTF tokens in all forms
  - **Authorization** - @admin_required decorator on admin routes
  - **Session Security** - Session regeneration on login
  - **Input Validation** - Custom validators for all user inputs
  - **Rate Limiting** - Flask-Limiter on login routes (5/min)
  - **Secret Key** - Production validation in config
  - **IDOR Protection** - Verified secure with get_or_404()

**Remaining Phase 4 Tasks**: Performance optimization (database indexes, N+1 queries, transaction rollback)

**Next Steps**:
- Complete remaining 3 performance tasks
- End-to-end security testing
- Deploy to Render.com for testing

**Progress**: ~85% complete (core functionality + security hardening done, performance optimization and deployment pending)