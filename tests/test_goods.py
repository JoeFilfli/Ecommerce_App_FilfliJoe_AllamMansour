# tests/test_goods.py

def test_add_goods(client, admin_token):
    """Test adding new goods as admin."""
    response = client.post('/goods', json={
        'name': 'Laptop',
        'category': 'electronics',
        'price_per_item': 999.99,
        'description': 'A high-end gaming laptop.',
        'count_in_stock': 10
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Goods added successfully.'
    assert 'goods_id' in data

def test_add_goods_unauthorized(client, regular_user_token):
    """Test adding goods as a regular user (should fail)."""
    response = client.post('/goods', json={
        'name': 'Smartphone',
        'category': 'electronics',
        'price_per_item': 499.99,
        'description': 'Latest model smartphone.',
        'count_in_stock': 20
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert response.status_code == 403
    data = response.get_json()
    assert data['error'] == 'Unauthorized access.'

def test_get_all_goods(client, admin_token):
    """Test retrieving all goods."""
    # Add goods first
    response_add = client.post('/goods', json={
        'name': 'Headphones',
        'category': 'electronics',
        'price_per_item': 199.99,
        'description': 'Noise-cancelling headphones.',
        'count_in_stock': 15
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert response_add.status_code == 201  # Ensure goods were added successfully

    # Retrieve all goods
    response = client.get('/goods')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least one goods exists

def test_update_goods(client, admin_token):
    """Test updating existing goods."""
    # Add goods first
    add_response = client.post('/goods', json={
        'name': 'Tablet',
        'category': 'electronics',
        'price_per_item': 299.99,
        'description': '10-inch display tablet.',
        'count_in_stock': 25
    }, headers={'Authorization': f'Bearer {admin_token}'})
    goods_id = add_response.get_json()['goods_id']
    assert add_response.status_code == 201

    # Update goods
    update_response = client.put(f'/goods/{goods_id}', json={
        'price_per_item': 279.99,
        'count_in_stock': 30
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert update_response.status_code == 200
    data = update_response.get_json()
    assert data['message'] == 'Goods updated successfully.'

def test_delete_goods(client, admin_token):
    """Test deleting goods."""
    # Add goods first
    add_response = client.post('/goods', json={
        'name': 'Camera',
        'category': 'electronics',
        'price_per_item': 599.99,
        'description': 'Digital SLR camera.',
        'count_in_stock': 5
    }, headers={'Authorization': f'Bearer {admin_token}'})
    goods_id = add_response.get_json()['goods_id']
    assert add_response.status_code == 201

    # Delete goods
    delete_response = client.delete(f'/goods/{goods_id}', headers={'Authorization': f'Bearer {admin_token}'})
    assert delete_response.status_code == 200
    data = delete_response.get_json()
    assert data['message'] == 'Goods deleted successfully.'
    
    # Verify deletion
    get_response = client.get(f'/goods/{goods_id}')
    assert get_response.status_code == 404
    data = get_response.get_json()
    assert data['error'] == 'Goods not found.'
