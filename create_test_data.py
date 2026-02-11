from app import create_app, db
from app.models import User, Course, Attendance
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    print("Creating users...")
    
    # Create a teacher
    teacher = User(username='teacher1', email='teacher@school.com', role='teacher')
    teacher.set_password('password123')
    db.session.add(teacher)
    
    # Create students
    student1 = User(username='student1', email='student1@school.com', role='student')
    student1.set_password('password123')
    
    student2 = User(username='student2', email='student2@school.com', role='student')
    student2.set_password('password123')
    
    student3 = User(username='student3', email='student3@school.com', role='student')
    student3.set_password('password123')
    
    db.session.add(student1)
    db.session.add(student2)
    db.session.add(student3)
    db.session.commit()
    
    print("Creating course...")
    
    # Create a course
    course = Course(name='Python Programming', code='CS101', teacher_id=teacher.id)
    db.session.add(course)
    db.session.commit()
    
    print("Creating attendance records...")
    
    # List of all students
    students = [student1, student2, student3]
    
    # Create 10 days of attendance records
    # IMPORTANT: Same dates for ALL students
    for i in range(10):
        attendance_date = datetime.now().date() - timedelta(days=i)
        
        # Mark attendance for ALL students on this date
        # student1: 8/10 present (80%)
        # student2: 6/10 present (60%)  
        # student3: 10/10 present (100%)
        
        # Student1 - mostly present
        status1 = 'present' if i < 8 else 'absent'
        record1 = Attendance(
            student_id=student1.id,
            course_id=course.id,
            date=attendance_date,
            status=status1
        )
        db.session.add(record1)
        
        # Student2 - borderline attendance
        status2 = 'present' if i < 6 else 'absent'
        record2 = Attendance(
            student_id=student2.id,
            course_id=course.id,
            date=attendance_date,
            status=status2
        )
        db.session.add(record2)
        
        # Student3 - perfect attendance
        record3 = Attendance(
            student_id=student3.id,
            course_id=course.id,
            date=attendance_date,
            status='present'
        )
        db.session.add(record3)
    
    db.session.commit()
    
    print("\n✅ Test data created successfully!\n")
    print("=" * 50)
    print("LOGIN CREDENTIALS:")
    print("=" * 50)
    print("Teacher: teacher1 / password123")
    print("Student: student1 / password123 (80% attendance)")
    print("Student: student2 / password123 (60% attendance)")
    print("Student: student3 / password123 (100% attendance)")
    print("=" * 50)
    print("\nAll students have 10 total classes")
    print("Attendance marked for the same 10 dates for everyone")
