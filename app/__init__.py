# app/__init__.py
from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS
from flask_socketio import SocketIO
import os  # Keep os for os.getenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions without the app instance yet
login = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
socketio = SocketIO()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True)

    # Load configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    # Set database URI with fallback
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # Fallback to default SQLite database
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/opportunities.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Email configuration
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
    app.config["MAIL_USE_TLS"] = os.getenv(
        "MAIL_USE_TLS", "True").lower() == "true"
    app.config["MAIL_USE_SSL"] = os.getenv(
        "MAIL_USE_SSL", "False").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

    # Initialize extensions WITH the app instance
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Configure Flask-Login settings
    login.login_view = "main.login"
    # It's good to have a message
    login.login_message = "Please log in to access this page."

    @login.unauthorized_handler
    def unauthorized_callback():
        return jsonify(message="Authentication is required to access this resource."), 401

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
