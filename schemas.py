from marshmallow import Schema, fields, validate

class CustomerSchema(Schema):
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
    id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True)
    goods_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=lambda x: x > 0)
    total_price = fields.Float(dump_only=True)
    purchase_date = fields.DateTime(dump_only=True)
    # Optionally, include nested fields
    goods = fields.Nested(GoodsSchema, only=['id', 'name', 'price_per_item'])



class ReviewSchema(Schema):
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