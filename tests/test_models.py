import pytest
from app.models import User, Opportunity, Report
from app import db
from werkzeug.security import check_password_hash


class TestUser:
    """Test cases for User model."""

    def test_user_creation(self, app):
        """Test user creation with basic fields."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            # Set password to avoid NULL constraint
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)

            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.role == 'user'  # default role
            assert user.is_active is True
            assert user.is_banned is False

    def test_user_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')

            assert user.password_hash is not None
            assert user.password_hash != 'password123'  # should be hashed
            assert user.check_password('password123') is True
            assert user.check_password('wrongpassword') is False

    def test_user_suspend_activate(self, app):
        """Test user suspension and activation."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            # Set password to avoid NULL constraint
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)

            # Test suspension
            user.suspend()
            assert user.is_active is False
            assert user.suspended_at is not None

            # Test activation
            user.activate()
            assert user.is_active is True
            assert user.suspended_at is None

    def test_user_role_promotion(self, app):
        """Test user role changes."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')

            # Test valid role promotion
            user.promote('moderator')
            assert user.role == 'moderator'

            user.promote('admin')
            assert user.role == 'admin'

            # Test invalid role (should not change)
            user.promote('invalid_role')
            assert user.role == 'admin'  # should remain unchanged

    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            repr_str = repr(user)
            assert 'User testuser' in repr_str
            assert 'Role: user' in repr_str


class TestOpportunity:
    """Test cases for Opportunity model."""

    def test_opportunity_creation(self, app, test_user):
        """Test opportunity creation."""
        with app.app_context():
            opportunity = Opportunity(
                title='Test Opportunity',
                description='This is a test opportunity',
                category='Education',
                location='Test City',
                user_id=test_user.id
            )

            assert opportunity.title == 'Test Opportunity'
            assert opportunity.description == 'This is a test opportunity'
            assert opportunity.category == 'Education'
            assert opportunity.location == 'Test City'
            assert opportunity.user_id == test_user.id
            assert opportunity.is_approved is False  # default
            assert opportunity.approved_by is None

    def test_opportunity_relationship(self, app, test_user):
        """Test opportunity-user relationship."""
        with app.app_context():
            opportunity = Opportunity(
                title='Test Opportunity',
                description='This is a test opportunity',
                category='Education',
                location='Test City',
                user_id=test_user.id
            )
            db.session.add(opportunity)
            db.session.commit()

            assert opportunity.user == test_user
            assert opportunity in test_user.opportunities

    def test_opportunity_repr(self, app, test_user):
        """Test opportunity string representation."""
        with app.app_context():
            opportunity = Opportunity(
                title='Test Opportunity',
                description='This is a test opportunity',
                category='Education',
                location='Test City',
                user_id=test_user.id
            )
            repr_str = repr(opportunity)
            assert 'Opportunity Test Opportunity' in repr_str


class TestReport:
    """Test cases for Report model."""

    def test_report_creation_user(self, app, test_user):
        """Test report creation for a user."""
        with app.app_context():
            report = Report(
                reporter_id=test_user.id,
                reported_user_id=test_user.id,
                reason='Test report for user'
            )

            assert report.reporter_id == test_user.id
            assert report.reported_user_id == test_user.id
            assert report.reported_opportunity_id is None
            assert report.reason == 'Test report for user'
            assert report.is_reviewed is False

    def test_report_creation_opportunity(self, app, test_user, test_opportunity):
        """Test report creation for an opportunity."""
        with app.app_context():
            report = Report(
                reporter_id=test_user.id,
                reported_opportunity_id=test_opportunity.id,
                reason='Test report for opportunity'
            )

            assert report.reporter_id == test_user.id
            assert report.reported_user_id is None
            assert report.reported_opportunity_id == test_opportunity.id
            assert report.reason == 'Test report for opportunity'

    def test_report_relationships(self, app, test_user, test_opportunity):
        """Test report relationships."""
        with app.app_context():
            report = Report(
                reporter_id=test_user.id,
                reported_opportunity_id=test_opportunity.id,
                reason='Test report'
            )
            db.session.add(report)
            db.session.commit()

            assert report.reporter == test_user
            assert report.reported_opportunity == test_opportunity
            assert report in test_user.reports_made
            assert report in test_opportunity.reports

    def test_report_repr(self, app, test_user):
        """Test report string representation."""
        with app.app_context():
            report = Report(
                reporter_id=test_user.id,
                reason='Test report'
            )
            repr_str = repr(report)
            assert 'Report' in repr_str
            assert str(test_user.id) in repr_str
