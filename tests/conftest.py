# tests/conftest.py

import pytest
from app import app as flask_app
from models import db, Customer
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='session')
def app():
    """Fixture to initialize the Flask app for testing."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test_jwt_secret_key"
    })
    with flask_app.app_context():
        db.create_all()
        # Create an admin user
        admin_user = Customer(
            full_name='Admin User',
            username='admin',
            password=generate_password_hash('AdminPass123!'),
            age=30,
            address='Admin Address',
            gender='Other',
            marital_status='Single',
            wallet_balance=0.0,
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
    yield flask_app
    # Teardown
    with flask_app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """Fixture to create a test client."""
    return app.test_client()

@pytest.fixture
def admin_token(client):
    """Fixture to get JWT token for admin user."""
    response = client.post('/customers/login', json={
        'username': 'admin',
        'password': 'AdminPass123!'
    })
    data = response.get_json()
    return data['access_token']

@pytest.fixture
def regular_user_token(client):
    """Fixture to create a regular user and get JWT token."""
    # Register a new user
    client.post('/customers/register', json={
        'full_name': 'Test User',
        'username': 'testuser',
        'password': 'TestPass123!',
        'age': 25,
        'address': 'Test Address',
        'gender': 'Male',
        'marital_status': 'Single'
    })
    # Login to get token
    response = client.post('/customers/login', json={
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    data = response.get_json()
    return data['access_token']
