# schemas.py

from marshmallow import Schema, fields, validate

class CustomerSchema(Schema):
    """
    Schema for serializing and deserializing Customer instances.

    Attributes:
        id (int): Customer ID (read-only).
        full_name (str): Full name of the customer.
        username (str): Username of the customer.
        password (str): Password for the customer (write-only).
        age (int): Age of the customer.
        address (str): Address of the customer.
        gender (str): Gender of the customer.
        marital_status (str): Marital status of the customer.
        wallet_balance (float): Wallet balance of the customer (read-only).
        is_admin (bool): Admin status of the customer (read-only).
    """

    id = fields.Int(dump_only=True)
    full_name = fields.Str(required=True, validate=validate.Length(min=1))
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(load_only=True, required=True)
    age = fields.Int(required=True, validate=lambda x: x > 0)
    address = fields.Str(required=True)
    gender = fields.Str(validate=validate.OneOf(['Male', 'Female', 'Other']))
    marital_status = fields.Str(validate=validate.OneOf(['Single', 'Married', 'Divorced', 'Widowed']))
    wallet_balance = fields.Float(dump_only=True)
    is_admin = fields.Bool(dump_only=True)


class GoodsSchema(Schema):
    """
    Schema for serializing and deserializing Goods instances.

    Attributes:
        id (int): Goods ID (read-only).
        name (str): Name of the goods.
        category (str): Category of the goods.
        price_per_item (float): Price per item.
        description (str): Description of the goods.
        count_in_stock (int): Number of items in stock.
    """

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    category = fields.Str(
        required=True,
        validate=validate.OneOf(['food', 'clothes', 'accessories', 'electronics'])
    )
    price_per_item = fields.Float(required=True)
    description = fields.Str()
    count_in_stock = fields.Int(required=True, validate=lambda x: x >= 0)


class PurchaseSchema(Schema):
    """
    Schema for serializing and deserializing Purchase instances.

    Attributes:
        id (int): Purchase ID (read-only).
        customer_id (int): ID of the customer making the purchase.
        goods_id (int): ID of the goods being purchased.
        quantity (int): Quantity of goods purchased.
        total_price (float): Total price of the purchase (read-only).
        purchase_date (datetime): Date and time of purchase (read-only).
        goods (GoodsSchema): Nested schema for the goods.
    """

    id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True)
    goods_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=lambda x: x > 0)
    total_price = fields.Float(dump_only=True)
    purchase_date = fields.DateTime(dump_only=True)
    # Optionally, include nested fields
    goods = fields.Nested(GoodsSchema, only=['id', 'name', 'price_per_item'])


class ReviewSchema(Schema):
    """
    Schema for serializing and deserializing Review instances.

    Attributes:
        id (int): Review ID (read-only).
        customer_id (int): ID of the customer who submitted the review (read-only).
        goods_id (int): ID of the goods being reviewed.
        rating (int): Rating given to the goods (1-5).
        comment (str): Review comment.
        created_at (datetime): Date and time the review was created (read-only).
        is_moderated (bool): Moderation status of the review (read-only).
        customer (CustomerSchema): Nested schema for the customer (read-only).
        goods (GoodsSchema): Nested schema for the goods (read-only).
    """

    id = fields.Int(dump_only=True)
    customer_id = fields.Int(dump_only=True)
    goods_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    is_moderated = fields.Bool(dump_only=True)
    # Nested fields for detailed information
    customer = fields.Nested(CustomerSchema, only=['id', 'username'], dump_only=True)
    goods = fields.Nested(GoodsSchema, only=['id', 'name'], dump_only=True)
