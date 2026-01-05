# CBT Assessment Application

## Project Overview

This is a web-based Cognitive Behavioral Therapy (CBT) assessment tool designed for use in correctional treatment programs. It integrates evidence-based CBT principles with the 12-step recovery framework.

**Key Features:**
*   **Dual Login System:** Separate portals for Participants (State ID) and Admins/Clinicians.
*   **Assessment Workflow:** Participants complete 12-step assessments.
*   **Clinician Review:** Assessments must be reviewed and approved by an admin before the participant can advance to the next step.
*   **Dashboard:** Progress tracking for participants and review queues for admins.

**Technology Stack:**
*   **Language:** Python 3.12
*   **Framework:** Flask 3.1.2
*   **Database:** SQLAlchemy ORM with SQLite (Development) / PostgreSQL (Production).
*   **Authentication:** Flask-Login
*   **Frontend:** Jinja2 templates (HTML/CSS)
*   **Deployment:** AWS Elastic Beanstalk (Production) via GitHub Actions.

## Project Structure

*   `app/`: Core application package.
    *   `__init__.py`: Flask app factory and configuration.
    *   `models.py`: Database models (User, Admin, AssessmentAttempt, etc.).
    *   `routes.py`: Application controllers and view logic.
    *   `validators.py`: Input validation logic.
    *   `templates/`: HTML templates for the UI.
*   `config.py`: Configuration classes (Development, Production).
*   `init_db.py`: Script to initialize the database schema.
*   `create_test_data.py`: Script to seed the database with test users and admins.
*   `add_sample_assessment.py`: Script to seed Step 1 assessment questions.
*   `run.py`: Entry point for running the development server.
*   `DEPLOYMENT.md`: Detailed deployment instructions for AWS and Render.
*   `WORKFLOW_DESIGN.md`: Architecture and design decisions for the review workflow.

## Development Workflow

### Prerequisites
*   Python 3.10+
*   `pip`
*   Virtual environment recommended.

### Setup and Running

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Initialize Database:**
    ```bash
    python init_db.py
    ```

3.  **Seed Test Data:**
    ```bash
    python create_test_data.py
    python add_sample_assessment.py
    ```
    *   **Test Participant:** `TEST001` / `password123`
    *   **Test Admin:** `ADMIN001` / `admin123`

4.  **Run Application:**
    ```bash
    python run.py
    ```
    Access at `http://localhost:5000`.

### Database Schema
Key models in `app/models.py`:
*   `User`: Participants (State ID).
*   `Admin`: Clinicians/Supervisors.
*   `AssessmentAttempt`: Tracks a user's attempt at a step.
*   `Response`: User answers linked to an attempt.
*   `Step`, `Assessment`, `Question`: Content structure.

### Conventions
*   **Flask Blueprints:** Not currently used; routes are in a central `routes.py`.
*   **Templates:** Jinja2 templates inherit from `base.html`.
*   **Styles:** Currently using inline styles (TODO: move to static CSS).
*   **Security:** Uses Flask-WTF for CSRF, Flask-Limiter for rate limiting, and `@admin_required` decorators.

## Deployment

The project is configured for **AWS Elastic Beanstalk**.
*   **Config:** `.ebextensions/python.config`
*   **CI/CD:** `.github/workflows/deploy.yml` (Deploys on push to `main`).
*   **Production DB:** AWS RDS PostgreSQL.
*   See `DEPLOYMENT.md` for full details.

## AI Instructions
You are acting as a Senior Software Engineering Tutor. I am building this CBT Assessment Application to practice my Python, Flask, SQLAlchemy, and AWS skills.

**Tutoring Style:**
* **Don't Give Spoilers:** If I ask how to implement a feature (like the Clinician Review logic), explain the architectural pattern first. Do not write the full code unless I specifically ask for it.
* **Socratic Questioning:** Ask me how I plan to handle edge cases (e.g., "What happens if a Participant tries to access Step 2 before the Admin approves Step 1?").
* **Focus on Fundamentals:** Since I am a CS student, relate implementation choices back to Data Structures or SQL efficiency (e.g., "Why use an ORM here instead of raw SQL?").
* **Context Awareness:** Remember that this is a correctional treatment tool; keep the tone professional and security-conscious.
