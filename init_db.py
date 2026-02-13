from app import create_app, db
from app.models import User, Course
import os
import sys

# Detect if running on Render
is_production = os.environ.get('RENDER') or os.environ.get('DATABASE_URL')
config_name = 'production' if is_production else 'default'

print("=" * 60)
print(f"INITIALIZING DATABASE (Environment: {config_name})")
print("=" * 60)

app = create_app(config_name)

with app.app_context():
    try:
        # ALWAYS drop and recreate tables in production on startup
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        print("✅ Database tables created!")
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@attendance-system.com',
                role='teacher'
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            
            print("=" * 60)
            print("✅ ADMIN USER CREATED SUCCESSFULLY!")
            print("-" * 60)
            print("Username: admin")
            print("Password: Admin@123")
            print("=" * 60)
        else:
            print("ℹ️  Admin user already exists")
        
        # Create a sample course for demo
        course = Course.query.filter_by(code='DEMO101').first()
        if not course:
            course = Course(
                name='Demo Course',
                code='DEMO101',
                teacher_id=admin.id
            )
            db.session.add(course)
            db.session.commit()
            print("✅ Demo course created")
        
        print("\n✅ DATABASE INITIALIZATION COMPLETE!")
        sys.stdout.flush()  # Force output to show in Render logs
        
    except Exception as e:
        print(f"\n❌ ERROR DURING INITIALIZATION:")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        # Don't exit with error - let app start anyway
