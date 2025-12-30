import os

# Get the base directory of the app
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI') or f'sqlite:///{os.path.join(basedir, "instance", "cbt_assessment.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    def __init__(self):
        # Secret key is required in production to start normally
        if not os.environ.get('SECRET_KEY'):
            raise ValueError(
                "SECRET_KEY must be set in production! "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )

    DEBUG = False
