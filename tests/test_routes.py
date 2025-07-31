import pytest
from flask import url_for
from app import db
from app.models import User, Opportunity, Report


class TestAuthentication:
    """Test authentication routes."""

    def test_register_page(self, client):
        """Test registration page loads."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data

    def test_register_success(self, client, app):
        """Test successful user registration."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.check_password('password123')

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        response = client.post('/register', data={
            'username': 'testuser',  # same as test_user
            'email': 'different@example.com',
            'password': 'password123'
        })

        assert response.status_code == 200
        assert b'Username is already taken' in response.data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post('/register', data={
            'username': 'differentuser',
            'email': 'test@example.com',  # same as test_user
            'password': 'password123'
        })

        assert response.status_code == 200
        assert b'Email is already registered' in response.data

    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Login successful' in response.data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrongpassword'
        })

        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_logout(self, client, test_user):
        """Test logout functionality."""
        # First login
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })

        # Then logout
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'You have been logged out' in response.data


class TestOpportunityRoutes:
    """Test opportunity-related routes."""

    def test_index_page(self, client):
        """Test home page loads."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Community Connect' in response.data

    def test_new_opportunity_page_requires_login(self, client):
        """Test that new opportunity page requires login."""
        response = client.get('/new', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page

    def test_new_opportunity_with_login(self, client, test_user):
        """Test creating new opportunity when logged in."""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })

        response = client.post('/new', data={
            'title': 'Test Opportunity',
            'description': 'This is a test opportunity',
            'category': 'Education',
            'location': 'Test City'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Opportunity submitted for approval' in response.data

    def test_new_opportunity_missing_fields(self, client, test_user):
        """Test creating opportunity with missing fields."""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })

        response = client.post('/new', data={
            'title': 'Test Opportunity',
            # Missing description, category, location
        })

        assert response.status_code == 200
        assert b'All fields are required' in response.data

    def test_view_opportunity(self, client, test_opportunity):
        """Test viewing a specific opportunity."""
        response = client.get(f'/opportunity/{test_opportunity.id}')
        assert response.status_code == 200
        assert b'Test Opportunity' in response.data

    def test_dashboard_requires_login(self, client):
        """Test that dashboard requires login."""
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page

    def test_dashboard_with_login(self, client, test_user, test_opportunity):
        """Test dashboard when logged in."""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })

        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Test Opportunity' in response.data


class TestModerationRoutes:
    """Test moderation-related routes."""

    def test_moderate_opportunities_requires_moderator(self, client, test_user):
        """Test that moderation requires moderator role."""
        # Login as regular user
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })

        response = client.get('/moderator/opportunities')
        assert response.status_code == 403  # Forbidden

    def test_moderate_opportunities_as_moderator(self, client, test_moderator):
        """Test moderation page as moderator."""
        # Login as moderator
        client.post('/login', data={
            'username': 'moderator',
            'password': 'moderator123'
        })

        response = client.get('/moderator/opportunities')
        assert response.status_code == 200

    def test_approve_opportunity(self, client, test_moderator, test_user, app):
        """Test approving an opportunity."""
        with app.app_context():
            # Create an unapproved opportunity
            opportunity = Opportunity(
                title='Unapproved Opportunity',
                description='This needs approval',
                category='Education',
                location='Test City',
                user_id=test_user.id,
                is_approved=False
            )
            db.session.add(test_user)
            db.session.add(opportunity)
            db.session.commit()

            # Login as moderator
            client.post('/login', data={
                'username': 'moderator',
                'password': 'moderator123'
            })

            response = client.post(f'/moderator/approve/{opportunity.id}')
            assert response.status_code == 302  # Redirect

            opportunity = Opportunity.query.get(opportunity.id)
            assert opportunity.is_approved is True

    def test_reject_opportunity(self, client, test_moderator, app):
        """Test rejecting an opportunity."""
        # Create an unapproved opportunity
        with app.app_context():
            opportunity = Opportunity(
                title='Unapproved Opportunity',
                description='This needs approval',
                category='Education',
                location='Test City',
                user_id=test_moderator.id,
                is_approved=False
            )
            db.session.add(opportunity)
            db.session.commit()
            opp_id = opportunity.id

        # Login as moderator
        client.post('/login', data={
            'username': 'moderator',
            'password': 'moderator123'
        })

        response = client.post(f'/moderator/reject/{opp_id}')
        assert response.status_code == 302  # Redirect

        with app.app_context():
            opportunity = Opportunity.query.get(opp_id)
            assert opportunity is None  # Should be deleted


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_submit_report_requires_login(self, client):
        """Test that submitting report requires login."""
        response = client.post('/report', json={
            'reason': 'Test report',
            'reported_user_id': 1
        })
        assert response.status_code == 401  # Unauthorized

    def test_submit_report_success(self, client, test_user, test_opportunity):
        """Test successful report submission."""
        # Login first
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })

        response = client.post('/report', json={
            'reason': 'Test report',
            'reported_opportunity_id': test_opportunity.id
        })

        assert response.status_code == 201
        assert b'Report submitted' in response.data

    def test_view_reports_requires_moderator(self, client, test_user):
        """Test that viewing reports requires moderator role."""
        # Login as regular user
        client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        })

        response = client.get('/moderator/reports')
        assert response.status_code == 403  # Forbidden

    def test_view_reports_as_moderator(self, client, test_moderator, test_report):
        """Test viewing reports as moderator."""
        # Login as moderator
        client.post('/login', data={
            'username': 'moderator',
            'password': 'moderator123'
        })

        response = client.get('/moderator/reports')
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) > 0
        assert data[0]['reason'] == 'Test report'
