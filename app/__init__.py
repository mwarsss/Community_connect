# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_migrate import Migrate
import os  # Keep os for os.getenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions without the app instance yet
login = LoginManager()
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions WITH the app instance
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    # Configure Flask-Login settings
    login.login_view = "main.login"
    # It's good to have a message
    login.login_message = "Please log in to access this page."

    # Import and register Blueprints *after* app and db are initialized
    # This is crucial to prevent circular imports
    # Use an alias to avoid name conflict with the module itself
    from app.routes import main as main_blueprint
    from app.routes import moderator_bp  # Now safe to import

    app.register_blueprint(main_blueprint)
    app.register_blueprint(moderator_bp)

    # Import models to ensure they are registered with SQLAlchemy
    # This should also be done after db.init_app(app)
    from app import models

    return app
