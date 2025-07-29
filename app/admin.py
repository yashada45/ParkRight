from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import db, ParkingLot, ParkingSpot, User, Reservation
from functools import wraps
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

# FLASK LOGIN INTEGRATION AND SECURITY
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

# New parking lot
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
            for _ in range(new_max_spots - current_spots):
                new_spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(new_spot)
        elif new_max_spots < current_spots:
            # Query for spots that are available and have no reservations.
            removable_spots = ParkingSpot.query.outerjoin(Reservation).filter(
                ParkingSpot.lot_id == lot.id,
                ParkingSpot.status == 'A',
                Reservation.id == None
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

# View spots
@admin.route('/lots/<int:lot_id>/spots')
@login_required
@admin_required
def view_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    
    spots = ParkingSpot.query.options(
        db.joinedload(ParkingSpot.reservations).joinedload(Reservation.user)
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
    
# Delete spots
@admin.route('/spots/delete', methods=['POST'])
@login_required
@admin_required
def delete_spots():
    spot_ids_to_delete = request.form.getlist('spot_ids')
    lot_id = request.form.get('lot_id')

    if not lot_id:
        flash('An error occurred: Lot ID is missing.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if not spot_ids_to_delete:
        flash('No spots were selected for deletion.', 'warning')
        return redirect(url_for('admin.view_spots', lot_id=lot_id))

    deleted_count = 0
    for spot_id in spot_ids_to_delete:
        spot = ParkingSpot.query.get(spot_id)
        if spot and spot.status == 'A':
            db.session.delete(spot)
            deleted_count += 1
    
    if deleted_count > 0:
        lot = ParkingLot.query.get(lot_id)
        if lot:
            lot.max_spots -= deleted_count

    db.session.commit()
    
    if deleted_count > 0:
        flash(f'{deleted_count} spots were successfully deleted.', 'success')
    else:
        flash('No available spots were selected to delete.', 'info')

    return redirect(url_for('admin.view_spots', lot_id=lot_id))

# vacate spot
@admin.route('/spots/<int:spot_id>/release', methods=['POST'])
@login_required
@admin_required
def release_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    
    if spot.status == 'O':
        active_reservation = Reservation.query.filter_by(
            spot_id=spot.id, 
            leaving_timestamp=None
        ).first()

        if active_reservation:
            # End reservation, calculate cost, free the spot
            active_reservation.leaving_timestamp = datetime.utcnow()
            
            duration_seconds = (active_reservation.leaving_timestamp - active_reservation.parking_timestamp).total_seconds()
            duration_hours = max(duration_seconds / 3600, 1/60) # cost logic
            cost = duration_hours * spot.lot.price_per_hour
            active_reservation.cost = round(cost, 2)

            spot.status = 'A'
            db.session.commit()
            flash('Spot released successfully', 'success')
        else:
            flash('Could not find an active reservation for this spot.', 'danger')
    else:
        flash('This spot is not occupied.', 'warning')
        
    return redirect(url_for('admin.view_spots', lot_id=spot.lot_id))

# List users
@admin.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.filter_by(is_admin=False).order_by(User.full_name).all()
    
    users_data = []
    for user in users:
        active_reservation = Reservation.query.filter_by(
            user_id=user.id, 
            leaving_timestamp=None
        ).first()
        
        if active_reservation:
            spot = active_reservation.spot
            status_text = f"Currently Parked at {spot.lot.prime_location_name} (Spot #{spot.id})"
            status_class = "success"
        else:
            # 2. Check for any past reservations
            past_reservation = Reservation.query.filter_by(user_id=user.id).first()
            if past_reservation:
                status_text = "Previously Parked"
                status_class = "secondary"
            else:
                # 3. If no reservations at all
                status_text = "Never Parked"
                status_class = "light"

        users_data.append({
            'user': user,
            'status_text': status_text,
            'status_class': status_class
        })
        
    return render_template('admin/users.html', users_data=users_data)

# Reservation
@admin.route('/reservations')
@login_required
@admin_required
def list_reservations():
    all_reservations = Reservation.query.order_by(Reservation.id.desc()).all()
    return render_template('admin/reservations.html', reservations=all_reservations)
