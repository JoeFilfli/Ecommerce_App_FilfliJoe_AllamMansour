# models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Customer(db.Model):
    """
    Represents a customer in the e-commerce system.

    Attributes:
        id (int): Primary key.
        full_name (str): Full name of the customer.
        username (str): Unique username for login.
        password (str): Hashed password for authentication.
        age (int): Age of the customer.
        address (str): Address of the customer.
        gender (str): Gender of the customer.
        marital_status (str): Marital status of the customer.
        wallet_balance (float): Current wallet balance of the customer.
        is_admin (bool): Flag indicating if the customer has administrative privileges.
    """

    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10))
    marital_status = db.Column(db.String(10))
    wallet_balance = db.Column(db.Float, default=0.0)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """
        Returns a string representation of the Customer instance.

        Returns:
            str: Representation string.
        """
        return f'<Customer {self.username}>'


class Goods(db.Model):
    """
    Represents a goods item in the e-commerce system.

    Attributes:
        id (int): Primary key.
        name (str): Name of the goods.
        category (str): Category of the goods (e.g., food, clothes).
        price_per_item (float): Price per individual item.
        description (str): Description of the goods.
        count_in_stock (int): Number of items available in stock.
    """

    __tablename__ = 'goods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(
        db.String(50),
        nullable=False,
        # Optionally, enforce category choices at the database level
    )
    price_per_item = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    count_in_stock = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        """
        Returns a string representation of the Goods instance.

        Returns:
            str: Representation string.
        """
        return f'<Goods {self.name}>'


class Purchase(db.Model):
    """
    Represents a purchase made by a customer.

    Attributes:
        id (int): Primary key.
        customer_id (int): Foreign key referencing the Customer.
        goods_id (int): Foreign key referencing the Goods.
        quantity (int): Quantity of goods purchased.
        total_price (float): Total price for the purchase.
        purchase_date (datetime): Date and time when the purchase was made.
        customer (Customer): Relationship to the Customer.
        goods (Goods): Relationship to the Goods.
    """

    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship('Customer', backref=db.backref('purchases', lazy=True))
    goods = db.relationship('Goods', backref=db.backref('purchases', lazy=True))

    def __repr__(self):
        """
        Returns a string representation of the Purchase instance.

        Returns:
            str: Representation string.
        """
        return f'<Purchase {self.id}>'


class Review(db.Model):
    """
    Represents a review submitted by a customer for a goods item.

    Attributes:
        id (int): Primary key.
        customer_id (int): Foreign key referencing the Customer.
        goods_id (int): Foreign key referencing the Goods.
        rating (int): Rating given to the goods (1-5).
        comment (str): Review comment.
        created_at (datetime): Date and time when the review was created.
        is_moderated (bool): Flag indicating if the review has been moderated.
        customer (Customer): Relationship to the Customer.
        goods (Goods): Relationship to the Goods.
    """

    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_moderated = db.Column(db.Boolean, default=False)

    customer = db.relationship('Customer', backref=db.backref('reviews', lazy=True))
    goods = db.relationship('Goods', backref=db.backref('reviews', lazy=True))

    def __repr__(self):
        """
        Returns a string representation of the Review instance.

        Returns:
            str: Representation string.
        """
        return f'<Review {self.id} by Customer {self.customer_id}>'



class Wishlist(db.Model):
    """
    Represents a customer's wishlist entry.

    Attributes:
        id (int): Primary key.
        customer_id (int): Foreign key to Customer.
        goods_id (int): Foreign key to Goods.
    """
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)

    # Relationships (optional for easy querying)
    customer = db.relationship('Customer', backref=db.backref('wishlist_items', lazy=True))
    goods = db.relationship('Goods', backref=db.backref('wishlisted_by', lazy=True))

    def __repr__(self):
        return f'<Wishlist customer_id={self.customer_id} goods_id={self.goods_id}>'
