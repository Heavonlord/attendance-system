from app import create_app, db
from app.models import User, Course
import os

# Determine environment
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    config_name = 'production'
else:
    config_name = 'default'

app = create_app(config_name)

with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("✅ Database tables created!")
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            admin = User(
                username='admin',
                email='admin@attendance-system.com',
                role='teacher',
                roll_no=None
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created!")
            print("=" * 50)
            print("LOGIN CREDENTIALS:")
            print("Username: admin")
            print("Password: Admin@123")
            print("=" * 50)
        else:
            print("ℹ️ Admin user already exists")
        
        print("✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        # Don't fail the app startup, just log the error
        pass
