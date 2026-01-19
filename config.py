import os

# Get the base directory of the app
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or os.environ.get(
        'DATABASE_URI') or f'sqlite:///{os.path.join(basedir, "instance", "cbt_assessment.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Logging configuration
    LOG_DIR = os.path.join(basedir, 'logs')
    LOG_FILE = os.path.join(LOG_DIR, 'cbt_assessment.log')
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


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
