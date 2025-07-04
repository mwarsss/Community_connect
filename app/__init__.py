from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-key")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "your_development_secret_key"  # use env var in production

db = SQLAlchemy(app)

# fmt: off
from app.routes import register_routes  # Import after db is defined
from app.models import Opportunity  # Import models to register them with SQLAlchemy
# fmt: on
register_routes(app)

with app.app_context():
    db.create_all()
