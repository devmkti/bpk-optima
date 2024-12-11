# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.database import db

def create_app():
    app = Flask(__name__,)
    app.static_folder = 'views/static'
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)

    # Register blueprints/routes
    with app.app_context():
        from .routes import main_bp
        app.register_blueprint(main_bp)

        # Create database tables if not exists
        db.create_all()

    return app