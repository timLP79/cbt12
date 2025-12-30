from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
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


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_object('config.DevelopmentConfig')

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
