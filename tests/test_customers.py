import pytest
from app import app, db
from models import Customer

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_register_customer(client):
    response = client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testuser",
        "password": "TestPass123",
        "age": 25,
        "address": "123 Test St",
        "gender": "Other",
        "marital_status": "Single"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Customer registered successfully.'
    assert 'customer_id' in data

def test_register_existing_username(client):
    # First registration
    client.post('/customers/register', json={
        "full_name": "Test User",
        "username": "testuser",
        "password": "TestPass123",
        "age": 25,
        "address": "123 Test St"
    })
    # Attempt to register with the same username
    response = client.post('/customers/register', json={
        "full_name": "Another User",
        "username": "testuser",
        "password": "AnotherPass456",
        "age": 30,
        "address": "456 Test Ave"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Username already exists.'
