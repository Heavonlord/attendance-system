from app import create_app, db
from app.models import User, Course
import os

# Use production config
app = create_app('production')

with app.app_context():
    try:
        print("=" * 60)
        print("INITIALIZING DATABASE...")
        print("=" * 60)
        
        # Drop all tables and recreate (fresh start)
        db.drop_all()
        print("✅ Dropped all tables")
        
        db.create_all()
        print("✅ Created all tables")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@attendance-system.com',
            role='teacher'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        
        print("=" * 60)
        print("✅ ADMIN USER CREATED!")
        print("Username: admin")
        print("Password: Admin@123")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
