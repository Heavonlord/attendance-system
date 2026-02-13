from app import create_app, db
from app.models import User, Course, Attendance, Enrollment
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    print("=" * 60)
    print("Creating test data with enrollments...")
    print("=" * 60)
    
    # Create a teacher
    teacher = User(
        username='teacher1',
        email='teacher@school.com',
        role='teacher'
    )
    teacher.set_password('password123')
    db.session.add(teacher)
    db.session.commit()
    
    # Create students with roll numbers
    students_data = [
        ('Amal Kumar', 'student1@school.com', 'CS101'),
        ('Priya Singh', 'student2@school.com', 'CS102'),
        ('Rahul Verma', 'student3@school.com', 'CS103'),
        ('Sneha Reddy', 'student4@school.com', 'CS104'),
        ('Arjun Patel', 'student5@school.com', 'CS105'),
        ('Meera Nair', 'student6@school.com', 'CS106'),
        ('Karthik Raj', 'student7@school.com', 'CS107'),
        ('Anjali Sharma', 'student8@school.com', 'CS108'),
    ]
    
    students = []
    for name, email, roll_no in students_data:
        student = User(
            username=name,
            email=email,
            role='student',
            roll_no=roll_no
        )
        student.set_password('password123')
        students.append(student)
        db.session.add(student)
    
    db.session.commit()
    print(f"✅ Created {len(students)} students")
    
    # Create courses
    course1 = Course(
        name='Python Programming',
        code='CS101',
        teacher_id=teacher.id
    )
    course2 = Course(
        name='Data Structures',
        code='CS102',
        teacher_id=teacher.id
    )
    db.session.add(course1)
    db.session.add(course2)
    db.session.commit()
    print("✅ Created 2 courses")
    
    # Enroll students in courses
    # Course 1: First 5 students
    for i in range(5):
        enrollment = Enrollment(
            student_id=students[i].id,
            course_id=course1.id
        )
        db.session.add(enrollment)
    
    # Course 2: Last 5 students (some overlap)
    for i in range(3, 8):
        enrollment = Enrollment(
            student_id=students[i].id,
            course_id=course2.id
        )
        db.session.add(enrollment)
    
    db.session.commit()
    print("✅ Created enrollments")
    
    # Create 10 days of attendance for Course 1
    for day in range(10):
        attendance_date = datetime.now().date() - timedelta(days=day)
        
        # Enrolled students for course 1 (first 5)
        for i in range(5):
            # Varying attendance patterns
            if i == 0:  # 90%
                status = 'present' if day < 9 else 'absent'
            elif i == 1:  # 70%
                status = 'present' if day < 7 else 'absent'
            elif i == 2:  # 100%
                status = 'present'
            elif i == 3:  # 60%
                status = 'present' if day < 6 else 'absent'
            else:  # 80%
                status = 'present' if day < 8 else 'absent'
            
            record = Attendance(
                student_id=students[i].id,
                course_id=course1.id,
                date=attendance_date,
                status=status
            )
            db.session.add(record)
    
    # Create 10 days of attendance for Course 2
    for day in range(10):
        attendance_date = datetime.now().date() - timedelta(days=day)
        
        # Enrolled students for course 2 (students 3-7)
        for i in range(3, 8):
            status = 'present' if day < 7 else 'absent'  # 70% for all
            
            record = Attendance(
                student_id=students[i].id,
                course_id=course2.id,
                date=attendance_date,
                status=status
            )
            db.session.add(record)
    
    db.session.commit()
    print("✅ Created attendance records")
    
    print("\n" + "=" * 60)
    print("✅ TEST DATA CREATED SUCCESSFULLY!")
    print("=" * 60)
    print("\nLOGIN CREDENTIALS:")
    print("-" * 60)
    print("Teacher:")
    print("  Username: teacher1")
    print("  Password: password123")
    print("\nStudents (all password: password123):")
    for name, email, roll_no in students_data:
        print(f"  {name} ({roll_no}) - {email.split('@')[0]}")
    print("\nCourses:")
    print("  Python Programming (CS101) - 5 students enrolled")
    print("  Data Structures (CS102) - 5 students enrolled")
    print("=" * 60)
