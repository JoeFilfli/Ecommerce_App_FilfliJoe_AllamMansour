from models import Customer, Goods, Purchase, db
from sqlalchemy import func

def get_top_selling_goods(limit=5):
    """
    Fallback method: recommends top-selling items based on the number of purchases.
    """
    top_selling = (db.session.query(Goods)
                   .join(Purchase)
                   .group_by(Goods.id)
                   .order_by(func.count(Purchase.id).desc())
                   .limit(limit)
                   .all())
    return top_selling

def get_recommendations_for_customer(customer_id, limit=5):
    """
    Generate product recommendations for a given customer based on similar customer purchases.
    Steps:
    1. Get all goods the customer has purchased.
    2. Find other customers who have purchased these goods.
    3. Recommend goods those similar customers bought that the original customer hasn't yet purchased.
    4. If no similar customers or items are found, fallback to top selling goods.
    """

    # Goods that the target customer has already purchased
    purchased_goods_ids = db.session.query(Purchase.goods_id).filter(Purchase.customer_id == customer_id).all()
    purchased_goods_ids = [g_id for (g_id,) in purchased_goods_ids]

    # If the customer hasn't purchased anything, we have no basis for similarity, so fallback
    if not purchased_goods_ids:
        return get_top_selling_goods(limit=limit)

    # Find customers who purchased any of these goods
    similar_customers = (db.session.query(Purchase.customer_id)
                         .filter(Purchase.goods_id.in_(purchased_goods_ids), Purchase.customer_id != customer_id)
                         .group_by(Purchase.customer_id)
                         .all())
    similar_customers_ids = [c_id for (c_id,) in similar_customers]

    # If there are no similar customers, fallback
    if not similar_customers_ids:
        return get_top_selling_goods(limit=limit)

    # From these similar customers, find goods they purchased that our original customer hasn't
    recommended_goods = (db.session.query(Goods)
                         .join(Purchase)
                         .filter(Purchase.customer_id.in_(similar_customers_ids))
                         .filter(Goods.id.notin_(purchased_goods_ids))
                         .group_by(Goods.id)
                         .order_by(func.count(Purchase.id).desc())  # rank by popularity among similar customers
                         .limit(limit)
                         .all())

    # If no recommendations found, fallback to top sellers
    if not recommended_goods:
        return get_top_selling_goods(limit=limit)

    return recommended_goods
