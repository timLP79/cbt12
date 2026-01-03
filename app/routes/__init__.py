from flask import Flask
from .main import main
from .admin import admin


def register_blueprints(app: Flask):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(main)
    app.register_blueprint(admin)