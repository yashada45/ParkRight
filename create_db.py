from app import create_app, db
from app.models import User, ParkingLot, ParkingSpot, Reservation
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    
    existing_admin = User.query.filter_by(email='admin@vpapp.com').first()
    if not existing_admin:
        admin_user = User(
            email='admin@vpapp.com',
            full_name='Admin',
            password=generate_password_hash('admin123'), # Use a secure password in production
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")

    print("Database setup complete.")
