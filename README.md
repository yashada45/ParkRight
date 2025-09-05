# ParkRight - Vehicle Parking Management App 🅿️

---

## 📝 About The Project

ParkRight is a full-stack web application built with **Flask** and **SQLite** that provides a complete solution for managing vehicle parking lots.  
It features a robust role-based system for administrators and a seamless booking experience for users.

---

## 💻 Tech Stack

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)  
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)  
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)  
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)  
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)  
![Jinja](https://img.shields.io/badge/jinja-A91E1E.svg?style=for-the-badge&logo=jinja&logoColor=white)

---

## ✨ Features

### 👑 Admin Panel
- **Full CRUD Functionality**: Create, read, update, and delete parking lots.
- **Dynamic Spot Management**: Automatically manage parking spots based on lot capacity.
- **Live Monitoring**: View a real-time status table of every spot in a lot.
- **User Oversight**: See a complete list of all registered users and their status.
- **Global History**: Access a system-wide log of all parking reservations.

### 👤 User Dashboard
- **Simple Authentication**: Easy registration and login.
- **Real-Time Availability**: View live counts of available spots in all lots.
- **Parking Workflow**: A clear **Reserve → Occupy → Release** process.
- **Automated Billing**: Automatically calculates cost upon releasing a spot.
- **Personal History**: View a complete history of all personal parking sessions.

---

## 🚀 Getting Started

Follow these steps to get a local copy up and running.

### **Prerequisites**
- Python 3.8+
- Git

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/yashada45/ParkRight.git
   cd ParkRight
   ```

2. **Create and activate a virtual environment**

   **On Windows:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

   **On macOS / Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database and create the admin user**
   ```bash
   python create_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The app will be available at **http://127.0.0.1:5000**.

---

## 📖 Usage

Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.  
You can register as a new user or log in with the default admin credentials:

```
Email: admin@vpapp.com
Password: admin123
```

---

## 🌐 Contact

**Yashada Mathad** - [LinkedIn](https://linkedin.com/in/yashada-mathad-27131928b) - yashada45@gmail.com  

**Project Link:** [https://github.com/yashada45/ParkRight](https://github.com/yashada45/ParkRight)

