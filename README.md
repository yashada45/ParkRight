ParkRight - Vehicle Parking Management App
ParkRight is a full-stack web application built with Flask and SQLite that provides a complete solution for managing vehicle parking lots. It features a robust role-based system for administrators and a seamless booking experience for users.

Key Features
Admin Panel:

Full CRUD Functionality: Create, read, update, and delete parking lots.

Dynamic Spot Management: Automatically generate or remove parking spots when a lot's capacity is changed.

Live Monitoring: View a real-time status table of every spot in a lot (Available, Reserved, Occupied).

User Oversight: See a complete list of all registered users and their current parking status.

Reservation History: Access a global log of every parking reservation made in the system.

User Dashboard:

Simple Authentication: Easy registration and login for all users.

Real-Time Lot Availability: View a list of all parking lots with live counts of available spots.

Three-Step Parking Workflow: A clear Reserve -> Occupy -> Release process.

Automated Billing: The system automatically calculates the duration and final cost upon releasing a spot.

Personal History: Users can view a complete history of all their past and current parking sessions.

Technologies Used
Backend: Python, Flask, Flask-SQLAlchemy, Flask-Login

Database: SQLite

Frontend: HTML5, CSS3, Jinja2, Bootstrap 5

Password Security: Werkzeug

Setup and Installation
Follow these steps to get the project running on your local machine.

1. Prerequisites:

Python 3.8 or higher

Git

2. Clone the Repository:

git clone <your-repository-url>
cd vehicle-parking-app

3. Create and Activate a Virtual Environment:

Windows:

python -m venv venv
.\venv\Scripts\activate

macOS / Linux:

python3 -m venv venv
source venv/bin/activate

4. Install Dependencies:
Install all the required packages from the requirements.txt file.

pip install -r requirements.txt

5. Create the Database:
Run the create_db.py script to generate the app.db file and create the predefined admin user.

python create_db.py

You should see a message confirming that the database setup is complete and the admin user has been created.

6. Run the Application:
Start the Flask development server.

python app.py

The application will now be running at http://127.0.0.1:5000.

How to Use the Application
Navigate to http://127.0.0.1:5000 in your web browser.

You can either register a new user account or log in as the administrator.

Admin Credentials:

Email: admin@vpapp.com

Password: admin123

Issues Encountered & Resolutions
During development, several key issues were identified and resolved:

Database Integrity Error on Spot Deletion:

Issue: The application would crash with an IntegrityError when an admin tried to reduce a lot's capacity if a spot had a past reservation.

Resolution: The logic was fixed to only allow the deletion of spots that are both "Available" and have no associated reservation history, thus preserving data integrity.

Incorrect Occupancy Count:

Issue: The system incorrectly tracked occupied spots because the ParkingSpot model had a one-to-one relationship with Reservation, causing old reservation links to be overwritten.

Resolution: The model was corrected to a one-to-many relationship (one spot -> many reservations), and all functions were updated to query for the currently active reservation for a spot.

Nested HTML Forms Bug:

Issue: On the "View Spots" page, the "Release" button was incorrectly triggering the "Delete Spots" action.

Resolution: The nested <form> tag was removed, and the formaction attribute was used on the "Release" button to correctly point it to the release_spot route, resolving the conflict.