# app/models.py
from app import login  # Import the login manager instance
from app import db  # Correct way to import the SQLAlchemy instance
# Import LoginManager to decorate load_user
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  # Import datetime for timestamps


# Initialize LoginManager here if not done in __init__.py,
# but it's usually initialized in __init__.py and imported there for app.login.init_app(app)
# If login is already initialized in app/__init__.py, you might just need:
# from app import login # if you use @login.user_loader directly.

# It's good practice to define the User model first if other models (like Opportunity)
# have a foreign key relationship to it.

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Role can be 'user', 'moderator', 'admin'. Max length 20 is good.
    role = db.Column(db.String(20), default='user', nullable=False)
    # Ensure nullable=False for boolean defaults
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # Nullable as it's only set when suspended
    suspended_at = db.Column(db.DateTime, nullable=True)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    # Define a custom __init__ method for initial object creation
    # password_hash will be set by set_password method later.
    # is_active and suspended_at have defaults in Column definition.

    def __init__(self, username, email, role='user'):
        self.username = username
        self.email = email
        self.role = role

    # Method to set the user's password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check a provided password against the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Method to suspend a user account
    def suspend(self):
        self.is_active = False
        # Use parentheses here as it's a function call
        self.suspended_at = datetime.utcnow()

    # Method to reactivate a user account
    def activate(self):
        self.is_active = True
        self.suspended_at = None  # Clear suspension timestamp

    # Method to change a user's role
    def promote(self, new_role):
        # You might want to add validation here to ensure new_role is a valid role string
        valid_roles = ['user', 'moderator', 'admin']
        if new_role in valid_roles:
            self.role = new_role
        else:
            # Handle invalid role, e.g., raise an error or log a warning
            print(
                f"Warning: Attempted to set invalid role '{new_role}' for user {self.username}")

    # Standard representation for debugging and logging
    def __repr__(self):
        return f"<User {self.username} (Role: {self.role}, Active: {self.is_active})>"


# Define model for Opportunity
class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    # Ensure nullable=False for consistency
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    # Use datetime.utcnow, ensure nullable=False
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    approved_by = db.Column(db.String(120), nullable=True)

    # Add the foreign key to link to the User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Define a relationship to the User model (optional, but very useful)
    user = db.relationship(
        'User', backref=db.backref('opportunities', lazy=True))

    def __init__(self, title, description, category, location, user_id, is_approved=False, approved_by=None):
        self.title = title
        self.description = description
        self.category = category
        self.location = location
        self.user_id = user_id
        self.is_approved = is_approved  # Initialize these fields
        self.approved_by = approved_by  # Initialize these fields

    def __repr__(self):
        return f"<Opportunity {self.title}>"


# This part is crucial for Flask-Login.
# Ensure 'login' (LoginManager instance) is available for this decorator.
# If 'login' is created in __init__.py, you'll need to import it here.
# Assuming 'login' is initialized in app/__init__.py and exported.


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# --- Functions (if still needed, though often integrated into routes/views) ---

# These functions are often better handled directly in your routes.py
# or by creating a dedicated service layer/repository pattern.
# If you keep them, make sure they don't cause new circular imports.
# I'll keep them as you provided them, but note they directly use 'db'
# which is globally available from 'from app import db'.


def add_opportunity(title, description, category, location, user_id, is_approved=False):
    # No need for get_db()
    opp = Opportunity(
        title=title,
        description=description,
        category=category,
        location=location,
        user_id=user_id,
        is_approved=is_approved  # Ensure is_approved is passed to Opportunity constructor
    )
    db.session.add(opp)
    db.session.commit()

# app/models.py


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=True)
    reported_opportunity_id = db.Column(
        db.Integer, db.ForeignKey('opportunity.id'), nullable=True)
    reason = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    reporter = db.relationship('User', foreign_keys=[
                               reporter_id], backref='reports_made')
    reported_user = db.relationship(
        'User', foreign_keys=[reported_user_id], backref='reports_received')
    reported_opportunity = db.relationship('Opportunity', backref='reports')
    is_reviewed = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, reporter_id, reported_user_id=None, reported_opportunity_id=None, reason=None):
        self.reporter_id = reporter_id
        self.reported_user_id = reported_user_id
        self.reported_opportunity_id = reported_opportunity_id
        self.reason = reason

    def __repr__(self):
        return f"<Report {self.id} by {self.reporter_id}>"


def get_opportunities(query=None):
    # No need for get_db()
    if not query:
        return db.session.query(Opportunity).all()
    # Renamed to avoid conflict with function arg
    query_param = f"%{query.lower()}%"
    return db.session.query(Opportunity).filter(
        (Opportunity.title.ilike(query_param)) |
        (Opportunity.category.ilike(query_param))
    ).all()
