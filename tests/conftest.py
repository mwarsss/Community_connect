import pytest
import tempfile
import os
from app import create_app, db
from app.models import User, Opportunity, Report


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_admin(app):
    """Create a test admin user."""
    with app.app_context():
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return admin


@pytest.fixture
def test_moderator(app):
    """Create a test moderator user."""
    with app.app_context():
        moderator = User(username='moderator',
                         email='moderator@example.com', role='moderator')
        moderator.set_password('moderator123')
        db.session.add(moderator)
        db.session.commit()
        return moderator


@pytest.fixture
def test_opportunity(app, test_user):
    """Create a test opportunity."""
    with app.app_context():
        opportunity = Opportunity(
            title='Test Opportunity',
            description='This is a test opportunity',
            category='Education',
            location='Test City',
            user_id=test_user.id,
            is_approved=True
        )
        db.session.add(opportunity)
        db.session.commit()
        return opportunity


@pytest.fixture
def test_report(app, test_user, test_opportunity):
    """Create a test report."""
    with app.app_context():
        report = Report(
            reporter_id=test_user.id,
            reported_opportunity_id=test_opportunity.id,
            reason='Test report'
        )
        db.session.add(report)
        db.session.commit()
        return report
