import pytest
from app import create_app, db
from app.models import User


def test_app_creation():
    """Test that the app can be created."""
    app = create_app()
    assert app is not None
    assert app.config['TESTING'] is False  # Default config


def test_database_creation(app):
    """Test that database tables can be created."""
    with app.app_context():
        db.create_all()
        # If we get here without errors, the tables were created successfully
        assert True


def test_user_creation_simple(app):
    """Test basic user creation."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Verify user was created
        found_user = User.query.filter_by(username='testuser').first()
        assert found_user is not None
        assert found_user.email == 'test@example.com'
        assert found_user.check_password('password123') is True
