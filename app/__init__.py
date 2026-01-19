from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
from logging.handlers import RotatingFileHandler


# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address
)


@login_manager.user_loader
def load_user(user_id):
    """
    Load user from session.
    Checks user_type in session to determine if loading a User or Admin.
    """
    from app.models import User, Admin

    user_type = session.get('user_type', 'participant')

    if user_type == 'admin':
        return Admin.query.get(user_id)
    else:
        return User.query.get(user_id)


def configure_logging(app):
    """Configure application logging"""
    # Create logs directory if it doesn't exist
    if not os.path.exists(app.config['LOG_DIR']):
        os.makedirs(app.config['LOG_DIR'])

    # Set up file handler with rotation
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=app.config['LOG_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT']
    )

    # Set logging format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)

    # Set logging level from config
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
    file_handler.setLevel(log_level)

    # Add handler to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)

    # Log application startup
    app.logger.info('CBT Assessment application startup')


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_object('config.DevelopmentConfig')

    # Configure logging
    configure_logging(app)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    csrf.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    return app
