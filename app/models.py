from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from datetime import datetime


def get_db():
    from app import db  # ✅ local import to avoid circular import
    return db

#

# Define model at top to avoid circular use


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.String(120), nullable=True)

    def __init__(self, title, description, category, location) -> None:
        self.title = title
        self.description = description
        self.category = category
        self.location = location


def add_opportunity(title, description, category, location):
    db = get_db()
    opp = Opportunity(
        title=title,
        description=description,
        category=category,
        location=location
    )
    db.session.add(opp)
    db.session.commit()


def get_opportunities(query=None):
    db = get_db()
    if not query:
        return db.session.query(Opportunity).all()
    query = f"%{query.lower()}%"
    return db.session.query(Opportunity).filter(
        (Opportunity.title.ilike(query)) |  # type: ignore
        (Opportunity.category.ilike(query))  # type: ignore
    ).all()


# Creation of the user model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    # Correct spelling here
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password)  # Corrected typo here!

    def check_password(self, password):
        # Corrected typo here!
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
