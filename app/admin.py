from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import db, ParkingLot, ParkingSpot, User, Reservation
from functools import wraps
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to restrict access to admin users only
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admins only! Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin dashboard
@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    lots = ParkingLot.query.order_by(ParkingLot.id).all()
    
    lots_data = []
    for lot in lots:
        occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
        lots_data.append({
            'details': lot,
            'occupied_spots': occupied_spots,
            'total_spots': lot.max_spots
        })
        
    return render_template('admin/dashboard.html', lots_data=lots_data)

# new parking lot
@admin.route('/lots/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lot():
    if request.method == 'POST':
        prime_location_name = request.form['prime_location_name']
        if isinstance(prime_location_name, tuple):
            prime_location_name = prime_location_name[0]
        lot = ParkingLot(
            prime_location_name=prime_location_name,
            address=request.form['address'],
            pin_code=request.form['pin_code'],
            price_per_hour=float(request.form['price_per_hour']),
            max_spots=int(request.form['max_spots'])
        )
        db.session.add(lot)
        db.session.commit()

        # Create spots
        for i in range(1, lot.max_spots + 1):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)
        db.session.commit()

        flash('Parking lot created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/lot_form.html')

# Edit parking lot
@admin.route('/lots/<int:lot_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == 'POST':
        lot.prime_location_name = request.form['prime_location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price_per_hour = float(request.form['price_per_hour'])
        
        # Get new_max_spots first
        new_max_spots = int(request.form['max_spots'])  # This line was missing
        current_spots = len(lot.spots)

        if new_max_spots > current_spots:
            # Add new spots
            for _ in range(new_max_spots - current_spots):
                new_spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(new_spot)
        elif new_max_spots < current_spots:
            # Remove extra spots if available
            removable_spots = ParkingSpot.query.filter_by(
                lot_id=lot.id, 
                status='A'
            ).limit(current_spots - new_max_spots).all()
            
            if len(removable_spots) == (current_spots - new_max_spots):
                for spot in removable_spots:
                    db.session.delete(spot)
            else:
                flash('Cannot reduce spots. Some are still occupied.', 'danger')
                return redirect(url_for('admin.edit_lot', lot_id=lot.id))

        lot.max_spots = new_max_spots
        db.session.commit()
        flash('Parking lot updated.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/lot_form.html', lot=lot)

# Delete parking lot
@admin.route('/lots/<int:lot_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied = any(spot.status == 'O' for spot in lot.spots)
    if occupied:
        flash('Cannot delete lot. Some spots are still occupied.', 'danger')
        return redirect(url_for('admin.dashboard'))

    # Delete all spots then the lot
    for spot in lot.spots:
        db.session.delete(spot)
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted.', 'success')
    return redirect(url_for('admin.dashboard'))

# view spots
@admin.route('/lots/<int:lot_id>/spots')
@login_required
@admin_required
def view_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    
    spots = ParkingSpot.query.options(
        db.joinedload(ParkingSpot.reservation).joinedload(Reservation.user)
    ).filter_by(lot_id=lot.id).order_by(ParkingSpot.id).all()
    
    occupied_count = sum(1 for spot in spots if spot.status == 'O')
    available_count = lot.max_spots - occupied_count
    
    return render_template(
        'admin/spots.html', 
        lot=lot, 
        spots=spots, 
        occupied_spots=occupied_count, 
        available_spots=available_count
    )

# vacate spot
@admin.route('/spots/<int:spot_id>/release', methods=['POST'])
@login_required
@admin_required
def release_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.status == 'O' and spot.reservation:
        # End reservation and free the spot
        spot.reservation.leaving_timestamp = datetime.utcnow()
        spot.status = 'A'
        db.session.commit()
        flash('Spot released successfully', 'success')
    return redirect(url_for('admin.view_spots', lot_id=spot.lot_id))

# List users
@admin.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.filter_by(is_admin=False).all()
    user_data = []
    
    # user data
    for user in users:
        latest_reservation = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.id.desc()).first()
        spot_status = 'N/A'
        if latest_reservation and latest_reservation.spot:
            spot_status = latest_reservation.spot.status
        user_data.append({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'spot_status': spot_status
        })
        
    return render_template('admin/users.html', users=user_data)
