from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_migrate import Migrate
import os


# Load environment variables from .env file
load_dotenv()

login = LoginManager()

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    login.login_view = "main.login"

    from app.routes import main
    app.register_blueprint(main)

    from app import models
    return app
