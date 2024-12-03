# tests/test_reviews.py

def test_submit_review_success(client, admin_token, regular_user_token):
    """Test submitting a review successfully."""
    # Add goods first
    add_response = client.post('/goods', json={
        'name': 'Smartwatch',
        'category': 'electronics',
        'price_per_item': 199.99,
        'description': 'A smartwatch with various features.',
        'count_in_stock': 25
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert add_response.status_code == 201  # Ensure goods were added successfully
    goods_id = add_response.get_json()['goods_id']
    
    # Submit review
    review_response = client.post('/reviews', json={
        'goods_id': goods_id,
        'rating': 5,
        'comment': 'Excellent product!'
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert review_response.status_code == 201
    data = review_response.get_json()
    assert data['message'] == 'Review submitted successfully.'
    assert 'review' in data
    assert data['review']['rating'] == 5
    assert data['review']['comment'] == 'Excellent product!'

def test_submit_duplicate_review(client, admin_token, regular_user_token):
    """Test submitting a duplicate review for the same product."""
    # Add goods first
    add_response = client.post('/goods', json={
        'name': 'Bluetooth Speaker',
        'category': 'electronics',
        'price_per_item': 59.99,
        'description': 'Portable Bluetooth speaker.',
        'count_in_stock': 30
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert add_response.status_code == 201  # Ensure goods were added successfully
    goods_id = add_response.get_json()['goods_id']
    
    # Submit first review
    first_review = client.post('/reviews', json={
        'goods_id': goods_id,
        'rating': 4,
        'comment': 'Good sound quality.'
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert first_review.status_code == 201
    
    # Attempt to submit duplicate review
    duplicate_response = client.post('/reviews', json={
        'goods_id': goods_id,
        'rating': 3,
        'comment': 'Changed my mind.'
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert duplicate_response.status_code == 400
    data = duplicate_response.get_json()
    assert data['error'] == 'You have already reviewed this product.'

def test_update_review_success(client, admin_token, regular_user_token):
    """Test updating an existing review."""
    # Add goods and submit a review first
    add_response = client.post('/goods', json={
        'name': 'Fitness Tracker',
        'category': 'accessories',
        'price_per_item': 99.99,
        'description': 'Tracks your fitness activities.',
        'count_in_stock': 40
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert add_response.status_code == 201  # Ensure goods were added successfully
    goods_id = add_response.get_json()['goods_id']
    
    review_response = client.post('/reviews', json={
        'goods_id': goods_id,
        'rating': 4,
        'comment': 'Very useful.'
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert review_response.status_code == 201
    review_id = review_response.get_json()['review']['id']
    
    # Update the review
    update_response = client.put(f'/reviews/{review_id}', json={
        'rating': 5,
        'comment': 'Actually, it\'s awesome!'
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert update_response.status_code == 200
    data = update_response.get_json()
    assert data['message'] == 'Review updated successfully.'
    assert data['review']['rating'] == 5
    assert data['review']['comment'] == "Actually, it's awesome!"

def test_delete_review_as_owner(client, admin_token, regular_user_token):
    """Test deleting a review as its owner."""
    # Add goods and submit a review first
    add_response = client.post('/goods', json={
        'name': 'E-reader',
        'category': 'electronics',
        'price_per_item': 129.99,
        'description': 'Read books electronically.',
        'count_in_stock': 20
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert add_response.status_code == 201  # Ensure goods were added successfully
    goods_id = add_response.get_json()['goods_id']
    
    review_response = client.post('/reviews', json={
        'goods_id': goods_id,
        'rating': 5,
        'comment': 'Love this e-reader!'
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert review_response.status_code == 201
    review_id = review_response.get_json()['review']['id']
    
    # Delete the review
    delete_response = client.delete(f'/reviews/{review_id}', headers={'Authorization': f'Bearer {regular_user_token}'})
    assert delete_response.status_code == 200
    data = delete_response.get_json()
    assert data['message'] == 'Review deleted successfully.'
    
    # Verify deletion
    get_response = client.get(f'/reviews/{review_id}')
    assert get_response.status_code == 404
    data = get_response.get_json()
    assert data['error'] == 'Review not found.'

def test_moderate_review_approve(client, admin_token, regular_user_token):
    """Test approving a review as admin."""
    # Add goods and submit a review first
    add_response = client.post('/goods', json={
        'name': 'Wireless Charger',
        'category': 'electronics',
        'price_per_item': 39.99,
        'description': 'Fast wireless charger.',
        'count_in_stock': 15
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert add_response.status_code == 201  # Ensure goods were added successfully
    goods_id = add_response.get_json()['goods_id']
    
    review_response = client.post('/reviews', json={
        'goods_id': goods_id,
        'rating': 3,
        'comment': 'It works fine.'
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert review_response.status_code == 201
    review_id = review_response.get_json()['review']['id']
    
    # Approve the review
    moderate_response = client.post(f'/reviews/{review_id}/moderate', json={
        'action': 'approve'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert moderate_response.status_code == 200
    data = moderate_response.get_json()
    assert data['message'] == 'Review has been approved.'

def test_moderate_review_flag(client, admin_token, regular_user_token):
    """Test flagging a review as admin."""
    # Add goods and submit a review first
    add_response = client.post('/goods', json={
        'name': 'USB-C Cable',
        'category': 'accessories',
        'price_per_item': 9.99,
        'description': 'Durable USB-C cable.',
        'count_in_stock': 100
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert add_response.status_code == 201  # Ensure goods were added successfully
    goods_id = add_response.get_json()['goods_id']

    review_response = client.post('/reviews', json={
        'goods_id': goods_id,
        'rating': 2,
        'comment': 'Stopped working after a week.'
    }, headers={'Authorization': f'Bearer {regular_user_token}'})
    assert review_response.status_code == 201
    review_id = review_response.get_json()['review']['id']

    # Flag the review
    moderate_response = client.post(f'/reviews/{review_id}/moderate', json={
        'action': 'flag'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert moderate_response.status_code == 200
    data = moderate_response.get_json()
    assert data['message'] == 'Review has been flagged.'
