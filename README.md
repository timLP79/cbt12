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
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # URL endpoints (coming next)
│   └── templates/           # HTML templates (coming next)
├── instance/
│   └── cbt_assessment.db    # SQLite database (not in git)
├── static/                  # CSS, JavaScript, images
├── venv/                    # Virtual environment (not in git)
├── config.py                # Configuration settings
├── init_db.py               # Database initialization script
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── .gitignore
```

## Database Schema

### Core Tables

- **Users**: Participant information (prison_id, name, current_step)
- **Steps**: The 12 recovery steps with descriptions
- **Assessments**: One assessment per step
- **Questions**: Individual questions (multiple choice or written)
- **MultipleChoiceOptions**: Answer choices for MC questions
- **Responses**: User answers with timestamps

## Features (Planned)

### Current Implementation
- ✅ Database models and relationships
- ✅ 12-step data seeding
- ✅ Configuration management
- ✅ Development environment setup

### In Development
- ⏳ User authentication system
- ⏳ Question-by-question assessment interface
- ⏳ Sequential step progression
- ⏳ Admin dashboard for reviewing responses

### Future Enhancements
- 📋 Progress tracking and visualization
- 📋 Offline capability for institutional tablets
- 📋 Data export for treatment records
- 📋 Multi-therapist support

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

5. **Run the application** (when ready)
```bash
   python run.py
```

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

**Project Status**: 🚧 Active Development - Database and models complete, building user interface next