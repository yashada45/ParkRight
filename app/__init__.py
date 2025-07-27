from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='../templates')

    # Loading configuration 
    app.config.from_object('config.Config')

    # initialising extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # configuring login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # import models
    from app import models
    
    # import and register blueprints
    from app.routes import main as main_blueprint
    from app.routes import auth
    from app.admin import admin as admin_blueprint
    
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth)
    app.register_blueprint(admin_blueprint)

    return app

