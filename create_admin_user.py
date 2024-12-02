from app import app, db
from models import Customer
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if admin user already exists
    admin_user = Customer.query.filter_by(username='admin').first()
    if not admin_user:
        hashed_password = generate_password_hash('AdminPass123!')
        admin_user = Customer(
            full_name='Admin User',
            username='admin',
            password=hashed_password,
            age=30,
            address='Admin Address',
            gender='Other',
            marital_status='Single',
            wallet_balance=0.0,
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")
