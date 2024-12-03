# tests/test_purchases.py

def test_make_purchase_success(client, admin_token, regular_user_token):
    """Test making a successful purchase."""
    # Add goods first
    add_response = client.post('/goods', json={
        'name': 'Book',
        'category': 'accessories',
        'price_per_item': 29.99,
        'description': 'A bestselling novel.',
        'count_in_stock': 50
    }, headers={'Authorization': f'Bearer {admin_token}'})
    goods_id = add_response.get_json()['goods_id']
    
    # Charge the user's wallet
    charge_response = client.post(f'/customers/testuser/wallet/charge', json={
        'amount': 100.0
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert charge_response.status_code == 200
    
    # Make purchase
    purchase_response = client.post('/sales', json={
        'goods_id': goods_id,
        'quantity': 2
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert purchase_response.status_code == 201
    data = purchase_response.get_json()
    assert data['message'] == 'Purchase successful.'
    assert 'purchase_id' in data
    assert data['wallet_balance'] == 100.0 - (29.99 * 2)

def test_make_purchase_insufficient_funds(client, admin_token, regular_user_token):
    """Test purchase failure due to insufficient funds."""
    # Add goods first
    add_response = client.post('/goods', json={
        'name': 'Gaming Console',
        'category': 'electronics',
        'price_per_item': 399.99,
        'description': 'Latest gaming console.',
        'count_in_stock': 10
    }, headers={'Authorization': f'Bearer {admin_token}'})
    goods_id = add_response.get_json()['goods_id']
    
    # Ensure wallet balance is 0
    purchase_response = client.post('/sales', json={
        'goods_id': goods_id,
        'quantity': 1
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert purchase_response.status_code == 400
    data = purchase_response.get_json()
    assert data['error'] == 'Insufficient funds in wallet.'

def test_make_purchase_insufficient_stock(client, admin_token, regular_user_token):
    """Test purchase failure due to insufficient stock."""
    # Add goods with limited stock
    add_response = client.post('/goods', json={
        'name': 'Limited Edition Item',
        'category': 'accessories',
        'price_per_item': 49.99,
        'description': 'Exclusive item.',
        'count_in_stock': 1
    }, headers={'Authorization': f'Bearer {admin_token}'})
    goods_id = add_response.get_json()['goods_id']
    
    # Charge the user's wallet sufficiently
    client.post(f'/customers/testuser/wallet/charge', json={
        'amount': 100.0
    }, headers={'Authorization': f'Bearer {admin_token}'})
    
    # Attempt to purchase more than available stock
    purchase_response = client.post('/sales', json={
        'goods_id': goods_id,
        'quantity': 2
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert purchase_response.status_code == 400
    data = purchase_response.get_json()
    assert data['error'] == 'Not enough items in stock.'
