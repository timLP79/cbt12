# CBT 12-Step Assessment Application

A web-based cognitive behavioral therapy (CBT) assessment tool integrated with the 12-step recovery program, designed for use in treatment facilities and correctional programs.

## Project Overview

This application combines evidence-based Cognitive Behavioral Therapy principles with the 12-step recovery framework to provide structured assessments for individuals in prison treatment programs. Each of the 12 steps has an associated assessment consisting of multiple-choice and written response questions.

## Purpose

- **Academic Learning Project**: Built to learn full-stack web development with Python/Flask
- **Real-world Application**: Designed for an ex-colleague working in correctional treatment programs
- **Progressive Assessment**: Users complete steps sequentially, tracking their recovery journey

## Technology Stack

- **Backend**: Python 3.12, Flask
- **Frontend**: Jinja2, Mobile Responsive CSS (Flexbox/Grid)
- **Database**: SQLite (development), PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Security**: Flask-WTF (CSRF), Flask-Limiter (Rate Limiting)
- **Production Server**: Gunicorn
- **Cloud Platform**: AWS Elastic Beanstalk
- **Database (Production)**: AWS RDS PostgreSQL
- **CI/CD**: GitHub Actions

## Project Structure
```
cbt-assessment/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── validators.py            # Input validation functions
│   ├── routes/                  # Route Blueprints
│   │   ├── main.py              # Participant flow
│   │   ├── admin.py             # Admin/Clinician flow
│   │   └── manage.py            # User management (CRUD)
│   ├── static/
│   │   └── css/
│   │       └── style.css        # Mobile responsive stylesheet
├── templates/               # HTML templates
│       ├── base.html            # Base template with common layout
│       ├── dashboard.html       # Participant dashboard
│       ├── user_profile.html    # Detailed participant profile
│       ├── manage_users_list.html # List of participant accounts
│       ├── manage_users_form.html # Form to create/edit participant accounts
│       ├── manage_admins_list.html # List of admin accounts
│       ├── manage_admins_form.html # Form to create/edit admin accounts
│       ├── question.html        # Assessment interface
│       └── ...                  # Other templates (login, admin_login, etc.)
├── .ebextensions/
│   └── python.config            # AWS Elastic Beanstalk configuration
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions deployment workflow
├── instance/                    # Local SQLite database
├── logs/                        # Application logs (rotating file handler)
├── config.py                    # Configuration classes
├── init_db.py                   # Database initialization
├── create_test_data.py          # Seeding script (Users/Admins)
├── add_full_assessments.py      # Seeding script (Steps 2-12 Content)
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── DEPLOYMENT.md                # AWS Deployment guide
└── TODO.md                      # Feature backlog
```

## Features

### ✅ Implemented

- **Authentication & User Management**
  - Dual login system (Participant vs. Admin)
  - Role-based access (Clinician vs. Supervisor)
  - Full CRUD for User and Admin management (Create, Read, Update, Deactivate, Reactivate)
  - User/Admin reactivation functionality (Issue #39)
  - Secure session handling (CSRF protection, session clearing on login)
  - Deactivated accounts blocked from login (Issue #26)

- **Assessment Workflow**
  - **Full Content**: Assessments for all 12 Steps (5 questions each)
  - **Resume Capability**: Users can save progress and resume later (pre-fills previous answers)
  - **Persistent State**: Assessment progress stored in database - survives session expiration (Issue #32)
    - Question order preserved across sessions (important for randomized assessments)
    - Users can logout/timeout and resume exactly where they left off
    - Never lose progress mid-assessment
  - **Review System**: Admins review submissions with "Approve" or "Request Revision" workflow
  - **History**: Detailed history of all past attempts and clinician feedback (accessible via Participant Profile)

- **Participant Experience**
  - Mobile-responsive dashboard showing progress and status
  - Visual feedback for "Pending Review", "Approved", or "Needs Revision"
  - Sequential step enforcement (must complete Step 1 to unlock Step 2)

- **Admin Portal**
  - Dashboard with queue of pending assessments
  - Detailed Participant Profiles showing enrollment stats and full history (view-only links pending)
  - Management tools for creating/deactivating users and admins

- **Modern UI Design (Issues #37, #38, #41)**
  - **Teal/Cyan Color Scheme**: Professional calming colors (#0891b2, #06b6d4)
  - **Dark Mode**: Full dark theme with toggle button (default mode)
  - **Excellent Contrast**: All pages optimized for readability in both themes (Issue #41)
  - **Bold Typography**: Gradient effects, modern letter spacing
  - **Smooth Animations**: Floating backgrounds, button shine effects, scale transforms
  - **CSS Variables**: Consistent theming with easy customization
  - **LocalStorage Persistence**: User theme preference saved across sessions
  - **Pure CSS**: No Bootstrap or frameworks, custom modern design

- **Technical Excellence**
  - **Mobile Responsive**: Fully optimized for phones and tablets
  - **Security**: CSRF protection, Rate Limiting (login routes only), **Strict State ID Validation**, Input Validation, Secure Headers
  - **Code Quality**: Blueprints architecture, Defensive Null Checks, Centralized CSS, Fix for Rate Limiter in development
  - **Transaction Management**: Proper rollback handling on all database operations (Issue #30)
  - **Database-Backed State**: Assessment progress persists across session expiration (Issue #32)
    - Question order and current position stored in database
    - Users never lose progress - can resume anytime
    - Session acts as performance cache with database as source of truth
  - **Logging System**: Comprehensive audit trail with rotating file handler (Issue #31)
    - Login/logout events (successful and failed attempts)
    - Database errors with context
    - Security events (403/404 errors, unauthorized access)
    - User management operations (create, update, deactivate, reactivate)
    - Assessment submissions and reviews
    - Configurable log levels (DEBUG for dev, INFO for production)
    - 10MB max file size with 10 backup files

### 📋 Future Improvements
- Advanced Analytics Dashboard
- Data Export (CSV/PDF)
- Offline Capability
- Database connection pooling optimization
- Email notifications for assessment status updates

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/timLP79/cbt12.git
   cd cbt12
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

4. **Initialize Database & Seed Data**
   ```bash
   # Initialize tables
   python init_db.py
   
   # Create test users (TEST001, ADMIN001)
   python create_test_data.py
   
   # Seed assessment content (Steps 2-12)
   python add_full_assessments.py
   ```

5. **Run the application**
   ```bash
   python run.py
   ```
   Access at `http://localhost:5000`

   **Test Credentials:**
   - **Participant:** `ID100001` / `Test123!`
   - **Admin (Supervisor):** `ADMIN001` / `Admin123!`

## Deployment

The application is configured for **AWS Elastic Beanstalk**.
See `DEPLOYMENT.md` for detailed instructions on deploying to production with RDS PostgreSQL.

## Project Management

**GitHub Project Board:** [CBT12 Project](https://github.com/users/timLP79/projects/10)

All development tasks, bugs, and enhancements are tracked in GitHub Issues and organized on our Kanban board.

### Current Status
- **Total Issues:** 42
  - ✅ Critical Fixed: 4 issues (#26-29 - Security & Bug Fixes)
  - ✅ UI Complete: 4 issues (#37 UI Redesign, #38 Dark Mode Contrast, #41 Assessment Complete Readability, #42 Button Alignment)
  - ✅ Bug Fixed: 1 issue (#40 Revision Response Loading)
  - ✅ Enhancements Complete: 5 issues (#36 Email Validation, #39 User Reactivation, #30 Transaction Management, #31 Logging System, #32 Database-Backed State)
  - 🟡 Medium: 3 issues (#33-35 remaining - Code Quality & Performance)
  - 📋 Backlog: 25 existing enhancement requests

### Key Documentation
- **TODO.md** - Technical debt and improvement backlog
- **WORKFLOW_DESIGN.md** - System architecture and design decisions
- **CBT_12Step_User_Guide.md** - End-user documentation

### Contributing
Issues are tracked with labels for priority (`critical`, `bug`, `enhancement`) and are assigned as work progresses. See `TODO.md` for detailed technical context on all open issues.

---

**Project Status**: **Phase 8 Complete (Jan 2026)**
- ✅ Core Functionality (Steps 1-12)
- ✅ Security Hardening
- ✅ Admin Dashboard & User Management
- ✅ User/Admin Reactivation (Issue #39)
- ✅ Email Validation with Library (Issue #36)
- ✅ Transaction Management with Rollbacks (Issue #30)
- ✅ Comprehensive Logging System (Issue #31)
- ✅ Database-Backed Assessment State (Issue #32)
- ✅ Mobile Responsiveness
- ✅ Modern UI Design with Dark Mode (Issues #37, #38, #41)
- ✅ Critical Bug Fixes (Issues #26-29, #40)
- ✅ AWS Deployment Infrastructure (Currently Paused to save costs)
- 🟢 **Ready for Production Deployment**
