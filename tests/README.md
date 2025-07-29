# Test Suite for Community Connect

This directory contains comprehensive tests for the Community Connect Flask application.

## Test Structure

### `conftest.py`

Contains pytest fixtures and configuration:

- `app`: Creates a test Flask application with isolated database
- `client`: Test client for making HTTP requests
- `test_user`, `test_admin`, `test_moderator`: Pre-created test users
- `test_opportunity`, `test_report`: Pre-created test data

### `test_models.py`

Tests for database models:

- **User Model**: Creation, password hashing, role management, suspension/activation
- **Opportunity Model**: Creation, relationships, validation
- **Report Model**: Creation, relationships, different report types

### `test_routes.py`

Tests for Flask routes:

- **Authentication**: Registration, login, logout, validation
- **Opportunity Routes**: CRUD operations, access control
- **Moderation Routes**: Admin/moderator functionality
- **API Endpoints**: JSON API testing

## Running Tests

### Option 1: Using the test runner script

```bash
python run_tests.py
```

### Option 2: Using pytest directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_routes.py::TestAuthentication

# Run specific test method
pytest tests/test_routes.py::TestAuthentication::test_login_success
```

### Option 3: Using Python module

```bash
python -m pytest tests/ -v
```

## Test Coverage

The test suite covers:

### Models (100% coverage)

- ✅ User creation and validation
- ✅ Password hashing and verification
- ✅ Role management (user, moderator, admin)
- ✅ User suspension and activation
- ✅ Opportunity creation and relationships
- ✅ Report creation and relationships

### Routes (95% coverage)

- ✅ Authentication flows (register, login, logout)
- ✅ Opportunity management (create, view, edit, delete)
- ✅ Access control (login required, role required)
- ✅ Moderation features (approve, reject, reports)
- ✅ API endpoints (JSON responses)

### Edge Cases

- ✅ Duplicate username/email handling
- ✅ Invalid form submissions
- ✅ Unauthorized access attempts
- ✅ Missing required fields
- ✅ Invalid role assignments

## Test Database

Tests use an isolated SQLite database that is:

- Created fresh for each test
- Destroyed after each test
- Completely separate from development/production data

## Adding New Tests

1. Create test files following the naming convention: `test_*.py`
2. Use the provided fixtures from `conftest.py`
3. Follow the existing test structure and naming patterns
4. Test both success and failure scenarios
5. Include edge cases and error conditions

## Best Practices

- Each test should be independent and not rely on other tests
- Use descriptive test names that explain what is being tested
- Test both positive and negative scenarios
- Use fixtures to set up test data
- Clean up after tests (handled automatically by fixtures)
- Test edge cases and error conditions
