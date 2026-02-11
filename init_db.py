from app import create_app, db
from app.models import User, Course

app = create_app('production')

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Database tables created!")
    
    # Create initial admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@attendance-system.com',
            role='teacher',
            roll_no=None
        )
        admin.set_password('ChangeThisPassword123!')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created!")
        print("Username: admin")
        print("Password: ChangeThisPassword123!")
    else:
        print("⚠️ Admin already exists")
