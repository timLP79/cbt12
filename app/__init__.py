from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    """
    Load user from session.
    Checks user_type in session to determine if loading a User or Clinician.
    """
    from app.models import User, Clinician

    user_type = session.get('user_type', 'participant')

    if user_type == 'clinician':
        return Clinician.query.get(user_id)
    else:
        return User.query.get(user_id)


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_object('config.DevelopmentConfig')

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
