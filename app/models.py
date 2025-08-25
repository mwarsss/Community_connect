# app/models.py
from app import login  # Import the login manager instance
from app import db  # Correct way to import the SQLAlchemy instance
# Import LoginManager to decorate load_user
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta  # Import datetime for timestamps
import secrets
import string


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
    account_active = db.Column(db.Boolean, default=True, nullable=False)
    # Nullable as it's only set when suspended
    suspended_at = db.Column(db.DateTime, nullable=True)
    is_banned = db.Column(db.Boolean, default=False, nullable=False)
    # Method to set the user's password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to check a provided password against the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Method to suspend a user account
    def suspend(self):
        self.account_active = False
        # Use parentheses here as it's a function call
        self.suspended_at = datetime.utcnow()

    # Method to reactivate a user account
    def activate(self):
        self.account_active = True
        self.suspended_at = None  # Clear suspension timestamp

    # Method to change a user's role
    def promote(self, new_role):
        # You might want to add validation here to ensure new_role is a valid role string
        valid_roles = ['user', 'moderator', 'admin']
        if new_role in valid_roles:
            self.role = new_role
            return True
        else:
            return False

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'account_active': self.account_active,
            'is_banned': self.is_banned,
        }

    # Standard representation for debugging and logging
    def __repr__(self):
        return f"<User {self.username} (Role: {self.role}, Active: {self.account_active})>"


class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)

    # Relationship to User
    user = db.relationship('User', backref=db.backref(
        'password_reset_tokens', lazy=True))

    def __init__(self, user_id, expires_in_hours=24):
        self.user_id = user_id
        self.token = self._generate_token()
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

    def _generate_token(self):
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))

    def is_valid(self):
        """Check if the token is still valid (not expired and not used)"""
        return not self.used and datetime.utcnow() < self.expires_at

    def mark_as_used(self):
        """Mark the token as used"""
        self.used = True

    def __repr__(self):
        return f"<PasswordResetToken {self.token[:8]}... for user {self.user_id}>"


# Define model for Opportunity
class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    # Relationship to User
    user = db.relationship(
        'User', backref=db.backref('opportunities', lazy=True), foreign_keys=[user_id])
    
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])

    tags = db.relationship('Tag', secondary='opportunity_tags', lazy='subquery',
        backref=db.backref('opportunities', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'location': self.location,
            'tags': [tag.name for tag in self.tags],
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat(),
            'approved_by': self.approved_by.username if self.approved_by else None,
            'user_id': self.user_id,
            'username': self.user.username,
            'reactions': [reaction.to_dict() for reaction in self.reactions],
            'bookmarks': [bookmark.to_dict() for bookmark in self.bookmarks],
        }

    def __repr__(self):
        return f"<Opportunity {self.title} by {self.user.username}>"


# Define model for Report
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    reported_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    reported_opportunity_id = db.Column(
        db.Integer, db.ForeignKey('opportunity.id'), nullable=True, index=True)
    reason = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    is_reviewed = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    reporter = db.relationship('User', foreign_keys=[
                               reporter_id], backref=db.backref('reports_made', lazy=True))
    reported_user = db.relationship('User', foreign_keys=[
                                    reported_user_id], backref=db.backref('reports_received', lazy=True))
    reported_opportunity = db.relationship(
        'Opportunity', backref=db.backref('reports', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_username': self.reporter.username,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'is_reviewed': self.is_reviewed,
            'reported_user': self.reported_user.to_dict() if self.reported_user else None,
            'reported_opportunity': self.reported_opportunity.to_dict() if self.reported_opportunity else None
        }

    def __repr__(self):
        return f"<Report {self.id} by {self.reporter.username}>"


class Reaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey(
        'opportunity.id'), nullable=False, index=True)
    # e.g., 'like', 'love', 'wow'
    reaction_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('reactions', lazy=True))
    opportunity = db.relationship(
        'Opportunity', backref=db.backref('reactions', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'opportunity_id': self.opportunity_id,
            'reaction_type': self.reaction_type,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Reaction {self.reaction_type} by {self.user.username} on {self.opportunity.title}>"


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey(
        'opportunity.id'), nullable=False, index=True)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('bookmarks', lazy=True))
    opportunity = db.relationship(
        'Opportunity', backref=db.backref('bookmarks', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'opportunity_id': self.opportunity_id,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<Bookmark by {self.user.username} on {self.opportunity.title}>"


opportunity_tags = db.Table('opportunity_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('opportunity_id', db.Integer, db.ForeignKey('opportunity.id'), primary_key=True)
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Tag {self.name}>"


# User loader for Flask-Login
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
