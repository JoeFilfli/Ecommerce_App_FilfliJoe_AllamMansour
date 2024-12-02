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

app = Flask(__name__)
app.config.from_object(config.Config)
db.init_app(app)
jwt = JWTManager(app)

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
    goods_list = Goods.query.all()
    result = goods_list_schema.dump(goods_list)
    return jsonify(result), 200


@app.route('/goods/<int:goods_id>', methods=['GET'])
def get_goods(goods_id):
    goods = Goods.query.get(goods_id)
    if not goods:
        return jsonify({'error': 'Goods not found.'}), 404
    result = goods_schema.dump(goods)
    return jsonify(result), 200


@app.route('/sales', methods=['POST'])
@jwt_required()
def make_sale():
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
        total_price=total_price
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
        comment=data.get('comment', '')
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
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()

    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found.'}), 404

    if review.customer_id != customer.id:
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
    current_username = get_jwt_identity()
    customer = Customer.query.filter_by(username=current_username).first()

    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found.'}), 404

    if review.customer_id != customer.id and not customer.is_admin:
        return jsonify({'error': 'You are not authorized to delete this review.'}), 403

    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted successfully.'}), 200

@app.route('/goods/<int:goods_id>/reviews', methods=['GET'])
def get_product_reviews(goods_id):
    goods = Goods.query.get(goods_id)
    if not goods:
        return jsonify({'error': 'Goods not found.'}), 404

    reviews = Review.query.filter_by(goods_id=goods_id).all()
    result = reviews_schema.dump(reviews)
    return jsonify(result), 200

@app.route('/customers/<string:username>/reviews', methods=['GET'])
@jwt_required()
def get_customer_reviews(username):
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
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review not found.'}), 404

    result = review_schema.dump(review)
    return jsonify(result), 200



if __name__ == '__main__':
    app.run(debug=True)
