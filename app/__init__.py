from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'  # Where to redirect if not logged in
login_manager.login_message = 'Please log in to access this page.'

def create_app(config_name='default'):
    """Application factory pattern"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints (routes)
    from app import routes
    app.register_blueprint(routes.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app