# tests/test_customers.py

def test_register_customer(client):
    """Test customer registration."""
    response = client.post('/customers/register', json={
        'full_name': 'John Doe',
        'username': 'johndoe',
        'password': 'Password123!',
        'age': 28,
        'address': '123 Main St',
        'gender': 'Male',
        'marital_status': 'Single'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Customer registered successfully.'
    assert 'customer_id' in data

def test_register_existing_username(client):
    """Test registration with an existing username."""
    # First registration
    client.post('/customers/register', json={
        'full_name': 'Jane Doe',
        'username': 'janedoe',
        'password': 'Password123!',
        'age': 25,
        'address': '456 Elm St',
        'gender': 'Female',
        'marital_status': 'Married'
    })
    # Attempt to register again with the same username
    response = client.post('/customers/register', json={
        'full_name': 'Jane Smith',
        'username': 'janedoe',  # Same username
        'password': 'NewPass123!',
        'age': 30,
        'address': '789 Oak St',
        'gender': 'Female',
        'marital_status': 'Divorced'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'Username already exists.'

def test_login_success(client, admin_token):
    """Test successful login."""
    response = client.post('/customers/login', json={
        'username': 'admin',
        'password': 'AdminPass123!'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data

def test_login_failure(client):
    """Test login with invalid credentials."""
    response = client.post('/customers/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == 'Invalid username or password.'
