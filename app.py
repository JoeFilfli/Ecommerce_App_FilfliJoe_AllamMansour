# app.py

"""
Ecommerce_FilfliJoe_AllamMansour Flask Application
===================================================

This module initializes and configures the Flask application, sets up the database,
JWT authentication, and defines the routes for managing customers, goods, purchases,
and reviews in the e-commerce platform.

Modules:
    - config: Configuration settings for the Flask app.
    - models: Database models for Customers, Goods, Purchases, and Reviews.
    - schemas: Marshmallow schemas for serializing and deserializing data.

Dependencies:
    - Flask: Web framework.
    - Flask_SQLAlchemy: ORM for database interactions.
    - Flask_JWT_Extended: JWT support for authentication.
    - Werkzeug: Security utilities for password hashing.
    - Marshmallow: Object serialization/deserialization.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import config
from models import db, Customer, Goods, Purchase, Review
from schemas import CustomerSchema, GoodsSchema, PurchaseSchema, ReviewSchema

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(config.Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Initialize Marshmallow schemas
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

goods_schema = GoodsSchema()
goods_list_schema = GoodsSchema(many=True)

purchase_schema = PurchaseSchema()
purchases_schema = PurchaseSchema(many=True)

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)


@app.route('/customers/register', methods=['POST'])
def register_customer():
    """
    Register a New Customer.

    This endpoint allows a new customer to register by providing necessary details.
    It validates the input data, hashes the password, and stores the customer in the database.

    **Endpoint:**
        POST /customers/register

    **Request JSON:**
        {
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "securepassword123",
            "age": 30,
            "address": "123 Main St, Anytown, USA",
            "gender": "Male",                # Optional
            "marital_status": "Single"       # Optional
        }

    **Responses:**
        201 Created:
            {
                "message": "Customer registered successfully.",
                "customer_id": 1
            }
        400 Bad Request:
            {
                "error": "Username already exists."
            }
            Or validation errors.
    """
    data = request.get_json()
    errors = customer_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    if Customer.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists.'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_customer = Customer(
        full_name=data['full_name'],
        username=data['username'],
        password=hashed_password,
        age=data['age'],
        address=data['address'],
        gender=data.get('gender'),
        marital_status=data.get('marital_status'),
        wallet_balance=0.0
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({
        'message': 'Customer registered successfully.',
        'customer_id': new_customer.id
    }), 201


@app.route('/customers/login', methods=['POST'])
def login():
    """
    Authenticate a Customer and Provide a JWT Token.

    This endpoint authenticates a customer using their username and password.
    Upon successful authentication, it returns a JWT access token for authorized access.

    **Endpoint:**
        POST /customers/login

    **Request JSON:**
        {
            "username": "johndoe",
            "password": "securepassword123"
        }

    **Responses:**
        200 OK:
            {
                "access_token": "jwt_token_here"
            }
        401 Unauthorized:
            {
                "error": "Invalid username or password."
            }
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    customer = Customer.query.filter_by(username=username).first()
    if customer and check_password_hash(customer.password, password):
        access_token = create_access_token(identity=customer.username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'error': 'Invalid username or password.'}), 401


@app.route('/customers/<string:username>', methods=['DELETE'])
@jwt_required()
def delete_customer(username):
    """
    Delete a Customer Account.

    This endpoint allows a customer to delete their own account. It ensures that the
    request is made by the account owner.

    **Endpoint:**
        DELETE /customers/<username>

    **Authentication:**
        - JWT token required.
        - Token must belong to the customer being deleted.

    **Responses:**
        200 OK:
            {
                "message": "Customer deleted successfully."
            }
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Customer not found."
            }
    """
    current_username = get_jwt_identity()
    if current_username != username:
        return jsonify({'error': 'Unauthorized access.'}), 403
    customer = Customer.query.filter_by(username=username).first()
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully.'}), 200
    else:
        return jsonify({'error': 'Customer not found.'}), 404


@app.route('/customers/<string:username>', methods=['PUT'])
@jwt_required()
def update_customer(username):
    """
    Update Customer Information.

    This endpoint allows a customer to update their own information. It ensures that the
    request is made by the account owner.

    **Endpoint:**
        PUT /customers/<username>

    **Authentication:**
        - JWT token required.
        - Token must belong to the customer being updated.

    **Request JSON:**
        {
            "full_name": "Jane Doe",           # Optional
            "age": 31,                          # Optional
            "address": "456 Elm St, Othertown",# Optional
            "gender": "Female",                 # Optional
            "marital_status": "Married"         # Optional
        }

    **Responses:**
        200 OK:
            {
                "message": "Customer information updated successfully."
            }
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Customer not found."
            }
    """
    current_username = get_jwt_identity()
    if current_username != username:
        return jsonify({'error': 'Unauthorized access.'}), 403
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404
    data = request.get_json()
    if 'full_name' in data:
        customer.full_name = data['full_name']
    if 'age' in data:
        customer.age = data['age']
    if 'address' in data:
        customer.address = data['address']
    if 'gender' in data:
        customer.gender = data['gender']
    if 'marital_status' in data:
        customer.marital_status = data['marital_status']
    db.session.commit()
    return jsonify({'message': 'Customer information updated successfully.'}), 200


@app.route('/customers', methods=['GET'])
@jwt_required()
def get_all_customers():
    """
    Retrieve All Customers.

    This endpoint allows an admin user to retrieve a list of all customers in the system.

    **Endpoint:**
        GET /customers

    **Authentication:**
        - JWT token required.
        - Token must belong to an admin user.

    **Responses:**
        200 OK:
            [
                {
                    "id": 1,
                    "full_name": "John Doe",
                    "username": "johndoe",
                    "age": 30,
                    "address": "123 Main St, Anytown, USA",
                    "gender": "Male",
                    "marital_status": "Single",
                    "wallet_balance": 0.0,
                    "is_admin": false
                },
                ...
            ]
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
    """
    current_user = get_jwt_identity()
    # Assuming you have an 'is_admin' field in your customer model
    customer = Customer.query.filter_by(username=current_user).first()
    if not customer.is_admin:
        return jsonify({'error': 'Unauthorized access.'}), 403
    customers = Customer.query.all()
    result = customers_schema.dump(customers)
    return jsonify(result), 200


@app.route('/customers/<string:username>', methods=['GET'])
@jwt_required()
def get_customer(username):
    """
    Retrieve a Specific Customer's Details.

    This endpoint allows a customer to retrieve their own details.

    **Endpoint:**
        GET /customers/<username>

    **Authentication:**
        - JWT token required.
        - Token must belong to the customer being retrieved.

    **Responses:**
        200 OK:
            {
                "id": 1,
                "full_name": "John Doe",
                "username": "johndoe",
                "age": 30,
                "address": "123 Main St, Anytown, USA",
                "gender": "Male",
                "marital_status": "Single",
                "wallet_balance": 0.0,
                "is_admin": false
            }
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Customer not found."
            }
    """
    current_username = get_jwt_identity()
    if current_username != username:
        return jsonify({'error': 'Unauthorized access.'}), 403

    customer = Customer.query.filter_by(username=username).first()
    if customer:
        result = customer_schema.dump(customer)
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Customer not found.'}), 404


@app.route('/customers/<string:username>/wallet/charge', methods=['POST'])
@jwt_required()
def charge_wallet(username):
    """
    Charge a Customer's Wallet.

    This endpoint allows an admin to add funds to a customer's wallet.

    **Endpoint:**
        POST /customers/<username>/wallet/charge

    **Authentication:**
        - JWT token required.
        - Token must belong to an admin user.

    **Request JSON:**
        {
            "amount": 50.0
        }

    **Responses:**
        200 OK:
            {
                "message": "$50.0 has been added to johndoe's wallet.",
                "wallet_balance": 50.0
            }
        400 Bad Request:
            {
                "error": "Invalid amount."
            }
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Customer not found."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()
    if not customer or not customer.is_admin:
        return jsonify({'error': 'Unauthorized access.'}), 403
    data = request.get_json()
    amount = data.get('amount')
    if amount is None or amount <= 0:
        return jsonify({'error': 'Invalid amount.'}), 400
    customer = Customer.query.filter_by(username=username).first()
    if customer:
        customer.wallet_balance += amount
        db.session.commit()
        return jsonify({
            'message': f'${amount} has been added to {username}\'s wallet.',
            'wallet_balance': customer.wallet_balance
        }), 200
    else:
        return jsonify({'error': 'Customer not found.'}), 404


@app.route('/customers/<string:username>/wallet/deduct', methods=['POST'])
@jwt_required()
def deduct_wallet(username):
    """
    Deduct Funds from a Customer's Wallet.

    This endpoint allows an admin to deduct funds from a customer's wallet.

    **Endpoint:**
        POST /customers/<username>/wallet/deduct

    **Authentication:**
        - JWT token required.
        - Token must belong to an admin user.

    **Request JSON:**
        {
            "amount": 20.0
        }

    **Responses:**
        200 OK:
            {
                "message": "$20.0 has been deducted from johndoe's wallet.",
                "wallet_balance": 30.0
            }
        400 Bad Request:
            {
                "error": "Invalid amount."
            }
            Or
            {
                "error": "Insufficient wallet balance."
            }
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Customer not found."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()
    if not customer or not customer.is_admin:
        return jsonify({'error': 'Unauthorized access.'}), 403
    data = request.get_json()
    amount = data.get('amount')
    if amount is None or amount <= 0:
        return jsonify({'error': 'Invalid amount.'}), 400
    customer = Customer.query.filter_by(username=username).first()
    if customer:
        if customer.wallet_balance >= amount:
            customer.wallet_balance -= amount
            db.session.commit()
            return jsonify({
                'message': f'${amount} has been deducted from {username}\'s wallet.',
                'wallet_balance': customer.wallet_balance
            }), 200
        else:
            return jsonify({'error': 'Insufficient wallet balance.'}), 400
    else:
        return jsonify({'error': 'Customer not found.'}), 404


@app.route('/goods', methods=['POST'])
@jwt_required()
def add_goods():
    """
    Add New Goods to the Inventory.

    This endpoint allows an admin user to add new goods to the inventory by providing
    necessary details.

    **Endpoint:**
        POST /goods

    **Authentication:**
        - JWT token required.
        - Token must belong to an admin user.

    **Request JSON:**
        {
            "name": "Laptop",
            "category": "electronics",
            "price_per_item": 999.99,
            "description": "A high-end gaming laptop.",
            "count_in_stock": 10
        }

    **Responses:**
        201 Created:
            {
                "message": "Goods added successfully.",
                "goods_id": 1
            }
        400 Bad Request:
            {
                "error": "Validation errors."
            }
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()
    if not customer or not customer.is_admin:
        return jsonify({'error': 'Unauthorized access.'}), 403

    data = request.get_json()
    errors = goods_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    new_goods = Goods(
        name=data['name'],
        category=data['category'],
        price_per_item=data['price_per_item'],
        description=data.get('description', ''),
        count_in_stock=data['count_in_stock']
    )

    db.session.add(new_goods)
    db.session.commit()
    return jsonify({
        'message': 'Goods added successfully.',
        'goods_id': new_goods.id
    }), 201


@app.route('/goods/<int:goods_id>', methods=['PUT'])
@jwt_required()
def update_goods(goods_id):
    """
    Update Existing Goods Information.

    This endpoint allows an admin user to update details of existing goods in the inventory.

    **Endpoint:**
        PUT /goods/<goods_id>

    **Authentication:**
        - JWT token required.
        - Token must belong to an admin user.

    **Request JSON:**
        {
            "name": "Gaming Laptop",              # Optional
            "category": "electronics",            # Optional
            "price_per_item": 1099.99,            # Optional
            "description": "An upgraded gaming laptop.", # Optional
            "count_in_stock": 8                    # Optional
        }

    **Responses:**
        200 OK:
            {
                "message": "Goods updated successfully."
            }
        400 Bad Request:
            {
                "error": "Validation errors."
            }
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Goods not found."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()
    if not customer or not customer.is_admin:
        return jsonify({'error': 'Unauthorized access.'}), 403

    goods = Goods.query.get(goods_id)
    if not goods:
        return jsonify({'error': 'Goods not found.'}), 404

    data = request.get_json()
    errors = goods_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    if 'name' in data:
        goods.name = data['name']
    if 'category' in data:
        goods.category = data['category']
    if 'price_per_item' in data:
        goods.price_per_item = data['price_per_item']
    if 'description' in data:
        goods.description = data['description']
    if 'count_in_stock' in data:
        goods.count_in_stock = data['count_in_stock']

    db.session.commit()
    return jsonify({'message': 'Goods updated successfully.'}), 200


@app.route('/goods/<int:goods_id>/deduct', methods=['POST'])
@jwt_required()
def deduct_goods(goods_id):
    """
    Deduct Items from Goods Stock.

    This endpoint allows an admin user to deduct a specified number of items from a goods' stock.

    **Endpoint:**
        POST /goods/<goods_id>/deduct

    **Authentication:**
        - JWT token required.
        - Token must belong to an admin user.

    **Request JSON:**
        {
            "amount": 2
        }

    **Responses:**
        200 OK:
            {
                "message": "2 items deducted from stock.",
                "count_in_stock": 8
            }
        400 Bad Request:
            {
                "error": "Invalid amount to deduct."
            }
            Or
            {
                "error": "Not enough items in stock to deduct."
            }
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Goods not found."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()
    if not customer or not customer.is_admin:
        return jsonify({'error': 'Unauthorized access.'}), 403

    goods = Goods.query.get(goods_id)
    if not goods:
        return jsonify({'error': 'Goods not found.'}), 404

    data = request.get_json()
    amount = data.get('amount', 1)
    if amount <= 0:
        return jsonify({'error': 'Invalid amount to deduct.'}), 400

    if goods.count_in_stock >= amount:
        goods.count_in_stock -= amount
        db.session.commit()
        return jsonify({
            'message': f'{amount} items deducted from stock.',
            'count_in_stock': goods.count_in_stock
        }), 200
    else:
        return jsonify({'error': 'Not enough items in stock to deduct.'}), 400


@app.route('/goods/<int:goods_id>', methods=['DELETE'])
@jwt_required()
def delete_goods(goods_id):
    """
    Delete a Goods Item.

    This endpoint allows an admin user to delete a goods item from the inventory.

    **Endpoint:**
        DELETE /goods/<goods_id>

    **Authentication:**
        - JWT token required.
        - Token must belong to an admin user.

    **Responses:**
        200 OK:
            {
                "message": "Goods deleted successfully."
            }
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Goods not found."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()
    if not customer or not customer.is_admin:
        return jsonify({'error': 'Unauthorized access.'}), 403

    goods = Goods.query.get(goods_id)
    if not goods:
        return jsonify({'error': 'Goods not found.'}), 404

    db.session.delete(goods)
    db.session.commit()
    return jsonify({'message': 'Goods deleted successfully.'}), 200


@app.route('/goods', methods=['GET'])
def get_all_goods():
    """
    Retrieve All Goods.

    This endpoint allows any user to retrieve a list of all goods available in the inventory.

    **Endpoint:**
        GET /goods

    **Responses:**
        200 OK:
            [
                {
                    "id": 1,
                    "name": "Laptop",
                    "category": "electronics",
                    "price_per_item": 999.99,
                    "description": "A high-end gaming laptop.",
                    "count_in_stock": 10
                },
                ...
            ]
    """
    goods_list = Goods.query.all()
    result = goods_list_schema.dump(goods_list)
    return jsonify(result), 200


@app.route('/goods/<int:goods_id>', methods=['GET'])
def get_goods(goods_id):
    """
    Retrieve Specific Goods Details.

    This endpoint allows any user to retrieve details of a specific goods item by its ID.

    **Endpoint:**
        GET /goods/<goods_id>

    **Responses:**
        200 OK:
            {
                "id": 1,
                "name": "Laptop",
                "category": "electronics",
                "price_per_item": 999.99,
                "description": "A high-end gaming laptop.",
                "count_in_stock": 10
            }
        404 Not Found:
            {
                "error": "Goods not found."
            }
    """
    goods = Goods.query.get(goods_id)
    if not goods:
        return jsonify({'error': 'Goods not found.'}), 404
    result = goods_schema.dump(goods)
    return jsonify(result), 200


@app.route('/sales', methods=['POST'])
@jwt_required()
def make_sale():
    """
    Make a Sale Purchase.

    This endpoint allows a customer to make a purchase of goods. It ensures sufficient stock
    and wallet balance before completing the transaction.

    **Endpoint:**
        POST /sales

    **Authentication:**
        - JWT token required.

    **Request JSON:**
        {
            "goods_id": 1,
            "quantity": 2
        }

    **Responses:**
        201 Created:
            {
                "message": "Purchase successful.",
                "purchase_id": 1,
                "wallet_balance": 980.02
            }
        400 Bad Request:
            {
                "error": "Not enough items in stock."
            }
            Or
            {
                "error": "Insufficient funds in wallet."
            }
        404 Not Found:
            {
                "error": "Customer not found."
            }
            Or
            {
                "error": "Goods not found."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404

    data = request.get_json()
    goods_id = data.get('goods_id')
    quantity = data.get('quantity', 1)
    if not goods_id:
        return jsonify({'error': 'Goods ID is required.'}), 400
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be at least 1.'}), 400

    goods = Goods.query.get(goods_id)
    if not goods:
        return jsonify({'error': 'Goods not found.'}), 404

    if goods.count_in_stock < quantity:
        return jsonify({'error': 'Not enough items in stock.'}), 400

    total_price = goods.price_per_item * quantity
    if customer.wallet_balance < total_price:
        return jsonify({'error': 'Insufficient funds in wallet.'}), 400

    # Deduct money from customer's wallet
    customer.wallet_balance -= total_price

    # Decrease count of purchased goods
    goods.count_in_stock -= quantity

    # Record the purchase
    new_purchase = Purchase(
        customer_id=customer.id,
        goods_id=goods.id,
        quantity=quantity,
        total_price=total_price,
        purchase_date=datetime.now(timezone.utc)
    )
    db.session.add(new_purchase)
    db.session.commit()

    return jsonify({
        'message': 'Purchase successful.',
        'purchase_id': new_purchase.id,
        'wallet_balance': customer.wallet_balance
    }), 201


@app.route('/customers/<string:username>/purchases', methods=['GET'])
@jwt_required()
def get_purchase_history(username):
    """
    Retrieve a Customer's Purchase History.

    This endpoint allows a customer to retrieve their own purchase history.

    **Endpoint:**
        GET /customers/<username>/purchases

    **Authentication:**
        - JWT token required.
        - Token must belong to the customer whose history is being retrieved.

    **Responses:**
        200 OK:
            [
                {
                    "id": 1,
                    "customer_id": 1,
                    "goods_id": 2,
                    "quantity": 3,
                    "total_price": 59.97,
                    "purchase_date": "2024-12-03T12:34:56Z"
                },
                ...
            ]
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Customer not found."
            }
    """
    current_username = get_jwt_identity()
    if current_username != username:
        return jsonify({'error': 'Unauthorized access.'}), 403

    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404

    purchases = Purchase.query.filter_by(customer_id=customer.id).all()
    result = purchases_schema.dump(purchases)
    return jsonify(result), 200


@app.route('/reviews', methods=['POST'])
@jwt_required()
def submit_review():
    """
    Submit a Review for a Goods Item.

    This endpoint allows a customer to submit a review for a specific goods item.
    It ensures that the customer has not already reviewed the same item.

    **Endpoint:**
        POST /reviews

    **Authentication:**
        - JWT token required.

    **Request JSON:**
        {
            "goods_id": 1,
            "rating": 5,
            "comment": "Excellent product!"
        }

    **Responses:**
        201 Created:
            {
                "message": "Review submitted successfully.",
                "review": {
                    "id": 1,
                    "customer_id": 1,
                    "goods_id": 1,
                    "rating": 5,
                    "comment": "Excellent product!",
                    "created_at": "2024-12-03T12:34:56Z",
                    "is_moderated": false
                }
            }
        400 Bad Request:
            {
                "error": "You have already reviewed this product."
            }
            Or validation errors.
        404 Not Found:
            {
                "error": "Goods not found."
            }
        404 Not Found:
            {
                "error": "Customer not found."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404

    data = request.get_json()
    errors = review_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    goods = Goods.query.get(data['goods_id'])
    if not goods:
        return jsonify({'error': 'Goods not found.'}), 404

    # Check if customer has already reviewed this product
    existing_review = Review.query.filter_by(customer_id=customer.id, goods_id=goods.id).first()
    if existing_review:
        return jsonify({'error': 'You have already reviewed this product.'}), 400

    new_review = Review(
        customer_id=customer.id,
        goods_id=goods.id,
        rating=data['rating'],
        comment=data.get('comment', ''),
        created_at=datetime.now(timezone.utc),
        is_moderated=False
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({
        'message': 'Review submitted successfully.',
        'review': review_schema.dump(new_review)
    }), 201


@app.route('/reviews/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """
    Update an Existing Review.

    This endpoint allows a customer to update their own review. Admins can update any review.

    **Endpoint:**
        PUT /reviews/<review_id>

    **Authentication:**
        - JWT token required.
        - If the requester is not an admin, they can only update their own reviews.

    **Request JSON:**
        {
            "rating": 4,                      # Optional
            "comment": "Updated comment."     # Optional
        }

    **Responses:**
        200 OK:
            {
                "message": "Review updated successfully.",
                "review": {
                    "id": 1,
                    "customer_id": 1,
                    "goods_id": 1,
                    "rating": 4,
                    "comment": "Updated comment.",
                    "created_at": "2024-12-03T12:34:56Z",
                    "is_moderated": false
                }
            }
        403 Forbidden:
            {
                "error": "You can only update your own reviews."
            }
        400 Bad Request:
            {
                "error": "Validation errors."
            }
        404 Not Found:
            {
                "error": "Review not found."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()

    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found.'}), 404

    # Check if the requester is the owner of the review or an admin
    if review.customer_id != customer.id and not customer.is_admin:
        return jsonify({'error': 'You can only update your own reviews.'}), 403

    data = request.get_json()
    errors = review_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    if 'rating' in data:
        review.rating = data['rating']
    if 'comment' in data:
        review.comment = data['comment']

    db.session.commit()
    return jsonify({'message': 'Review updated successfully.', 'review': review_schema.dump(review)}), 200


@app.route('/reviews/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """
    Delete a Review.

    This endpoint allows a customer to delete their own review or an admin to delete any review.

    **Endpoint:**
        DELETE /reviews/<review_id>

    **Authentication:**
        - JWT token required.
        - If the requester is not an admin, they can only delete their own reviews.

    **Responses:**
        200 OK:
            {
                "message": "Review deleted successfully."
            }
        403 Forbidden:
            {
                "error": "You are not authorized to delete this review."
            }
        404 Not Found:
            {
                "error": "Review not found."
            }
    """
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()

    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found.'}), 404

    # Check if the requester is the owner of the review or an admin
    if review.customer_id != customer.id and not customer.is_admin:
        return jsonify({'error': 'You are not authorized to delete this review.'}), 403

    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted successfully.'}), 200


@app.route('/goods/<int:goods_id>/reviews', methods=['GET'])
def get_product_reviews(goods_id):
    """
    Retrieve Reviews for a Specific Goods Item.

    This endpoint allows any user to retrieve all reviews associated with a specific goods item.

    **Endpoint:**
        GET /goods/<goods_id>/reviews

    **Responses:**
        200 OK:
            [
                {
                    "id": 1,
                    "customer_id": 1,
                    "goods_id": 1,
                    "rating": 5,
                    "comment": "Excellent product!",
                    "created_at": "2024-12-03T12:34:56Z",
                    "is_moderated": false
                },
                ...
            ]
        404 Not Found:
            {
                "error": "Goods not found."
            }
    """
    goods = Goods.query.get(goods_id)
    if not goods:
        return jsonify({'error': 'Goods not found.'}), 404

    reviews = Review.query.filter_by(goods_id=goods_id).all()
    result = reviews_schema.dump(reviews)
    return jsonify(result), 200


@app.route('/customers/<string:username>/reviews', methods=['GET'])
@jwt_required()
def get_customer_reviews(username):
    """
    Retrieve a Customer's Reviews.

    This endpoint allows a customer to retrieve all reviews they have submitted. Admins can retrieve any customer's reviews.

    **Endpoint:**
        GET /customers/<username>/reviews

    **Authentication:**
        - JWT token required.
        - If the requester is not an admin, they can only retrieve their own reviews.

    **Responses:**
        200 OK:
            [
                {
                    "id": 1,
                    "customer_id": 1,
                    "goods_id": 1,
                    "rating": 5,
                    "comment": "Excellent product!",
                    "created_at": "2024-12-03T12:34:56Z",
                    "is_moderated": false
                },
                ...
            ]
        403 Forbidden:
            {
                "error": "Unauthorized access."
            }
        404 Not Found:
            {
                "error": "Customer not found."
            }
    """
    current_username = get_jwt_identity()
    if current_username != username and not Customer.query.filter_by(username=current_username, is_admin=True).first():
        return jsonify({'error': 'Unauthorized access.'}), 403

    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404

    reviews = Review.query.filter_by(customer_id=customer.id).all()
    result = reviews_schema.dump(reviews)
    return jsonify(result), 200


@app.route('/reviews/<int:review_id>/moderate', methods=['POST'])
@jwt_required()
def moderate_review(review_id):
    """
    Moderate a Review.

    This endpoint allows an admin user to approve or flag a review.

    **Endpoint:**
        POST /reviews/<review_id>/moderate

    **Authentication:**
        - JWT token required.
        - Token must belong to an admin user.

    **Request JSON:**
        {
            "action": "approve"   # Or "flag"
        }

    **Responses:**
        200 OK:
            {
                "message": "Review has been approved."
            }
            Or
            {
                "message": "Review has been flagged."
            }
        400 Bad Request:
            {
                "error": "Invalid action. Use \"approve\" or \"flag\"."
            }
        403 Forbidden:
            {
                "error": "Only administrators can moderate reviews."
            }
        404 Not Found:
            {
                "error": "Review not found."
            }
    """
    current_username = get_jwt_identity()
    admin = Customer.query.filter_by(username=current_username, is_admin=True).first()
    if not admin:
        return jsonify({'error': 'Only administrators can moderate reviews.'}), 403

    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found.'}), 404

    data = request.get_json()
    action = data.get('action')
    if action not in ['approve', 'flag']:
        return jsonify({'error': 'Invalid action. Use "approve" or "flag".'}), 400

    if action == 'approve':
        review.is_moderated = True
    elif action == 'flag':
        review.is_moderated = False

    db.session.commit()
    return jsonify({'message': f'Review has been {action}d.'}), 200


@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review_details(review_id):
    """
    Retrieve Details of a Specific Review.

    This endpoint allows any user to retrieve detailed information about a specific review.

    **Endpoint:**
        GET /reviews/<review_id>

    **Responses:**
        200 OK:
            {
                "id": 1,
                "customer_id": 1,
                "goods_id": 1,
                "rating": 5,
                "comment": "Excellent product!",
                "created_at": "2024-12-03T12:34:56Z",
                "is_moderated": false
            }
        404 Not Found:
            {
                "error": "Review not found."
            }
    """
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found.'}), 404

    result = review_schema.dump(review)
    return jsonify(result), 200


if __name__ == '__main__':
    """
    Run the Flask Application.

    This entry point starts the Flask development server with debugging enabled.
    """
    app.run(debug=True)


