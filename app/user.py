from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, ParkingLot, ParkingSpot, Reservation
from datetime import datetime

user = Blueprint('user', __name__, url_prefix='/user')

# User Dashboard
@user.route('/dashboard')
@login_required
def dashboard():
    active_reservation = Reservation.query.filter(
        Reservation.user_id == current_user.id,
        Reservation.leaving_timestamp == None
    ).first()

    lots = ParkingLot.query.order_by(ParkingLot.id).all()
    lots_data = []
    for lot in lots:
        available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
        lots_data.append({
            'details': lot,
            'available_spots': available_spots
        })

    return render_template(
        'user/dashboard.html', 
        active_reservation=active_reservation, 
        lots_data=lots_data
    )

# Reserve spot
@user.route('/reserve', methods=['POST'])
@login_required
def reserve():
    # backend validation
    if Reservation.query.filter_by(user_id=current_user.id, leaving_timestamp=None).first():
        flash('You already have an active reservation.', 'danger')
        return redirect(url_for('user.dashboard'))

    lot_id = request.form.get('lot_id')
    first_available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()

    if first_available_spot:
        first_available_spot.status = 'R'
        
        new_reservation = Reservation(user_id=current_user.id, spot_id=first_available_spot.id)
        db.session.add(new_reservation)
        db.session.commit()
        
        return redirect(url_for('user.reservation_confirmation', reservation_id=new_reservation.id))
    else:
        flash('Sorry, no spots are available in this lot.', 'danger')
        return redirect(url_for('user.dashboard'))

# Reservation page
@user.route('/reserve/<int:reservation_id>')
@login_required
def reservation_confirmation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id:
        flash('This is not your reservation.', 'danger')
        return redirect(url_for('user.dashboard'))
        
    return render_template('user/reserve.html', reservation=reservation)

# Occupy spot
@user.route('/occupy/<int:reservation_id>', methods=['POST'])
@login_required
def occupy(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id or reservation.spot.status != 'R':
        flash('This reservation cannot be occupied at this time.', 'danger')
        return redirect(url_for('user.dashboard'))

    reservation.spot.status = 'O'
    reservation.parking_timestamp = datetime.utcnow()
    db.session.commit()
    
    flash('Spot occupied successfully! The parking timer has started.', 'success')
    return redirect(url_for('user.dashboard'))

# Release spot
@user.route('/release/<int:reservation_id>', methods=['POST'])
@login_required
def release(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.user_id != current_user.id or reservation.spot.status != 'O':
        flash('This reservation cannot be released at this time.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    # cost calculation logic for milestone
    reservation.leaving_timestamp = datetime.utcnow()
    
    duration_seconds = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds()
    duration_hours = max(duration_seconds / 3600, 1/60)
    cost = duration_hours * reservation.spot.lot.price_per_hour
    reservation.cost = round(cost, 2)

    reservation.spot.status = 'A'
    db.session.commit()
    
    flash(f'Spot released. Your total cost is ₹{reservation.cost:.2f}.', 'success')
    return redirect(url_for('user.history'))

# View Parking History
@user.route('/history')
@login_required
def history():
    user_reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.id.desc()).all()
    return render_template('user/history.html', reservations=user_reservations)
