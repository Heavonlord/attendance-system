from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from flask import send_file
import io
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Course, Attendance
from datetime import datetime

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.role == 'teacher':
                return redirect(url_for('main.teacher_dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@bp.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    """Teacher dashboard"""
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher_dashboard.html', courses=courses)

@bp.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard"""
    if current_user.role != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Get student's attendance records
    records = Attendance.query.filter_by(student_id=current_user.id).all()
    
    # Calculate attendance percentage
    total = len(records)
    present = len([r for r in records if r.status == 'present'])
    percentage = (present / total * 100) if total > 0 else 0
    
    return render_template('student_dashboard.html', 
                         records=records, 
                         percentage=round(percentage, 2))
@bp.route('/teacher/mark-attendance/<int:course_id>', methods=['GET', 'POST'])
@login_required
def mark_attendance(course_id):
    """Mark attendance for a course"""
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    
    # Verify teacher owns this course
    if course.teacher_id != current_user.id:
        flash('You do not have access to this course', 'danger')
        return redirect(url_for('main.teacher_dashboard'))
    
    if request.method == 'POST':
        date_str = request.form.get('date')
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get all students (for now, we'll use all students in the system)
        # In production, you'd have course enrollments
        students = User.query.filter_by(role='student').all()
        
        for student in students:
            status = request.form.get(f'status_{student.id}')
            if status:
                # Check if attendance already exists for this date
                existing = Attendance.query.filter_by(
                    student_id=student.id,
                    course_id=course_id,
                    date=attendance_date
                ).first()
                
                if existing:
                    existing.status = status
                else:
                    record = Attendance(
                        student_id=student.id,
                        course_id=course_id,
                        date=attendance_date,
                        status=status
                    )
                    db.session.add(record)
        
        db.session.commit()
        flash(f'Attendance marked for {len(students)} students', 'success')
        return redirect(url_for('main.teacher_dashboard'))
    
    # GET request - show form
    students = User.query.filter_by(role='student').all()
    today = datetime.now().date()
    
    return render_template('mark_attendance.html', 
                         course=course, 
                         students=students,
                         today=today)

@bp.route('/teacher/view-attendance/<int:course_id>')
@login_required
def view_course_attendance(course_id):
    """View all attendance records for a course"""
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    
    if course.teacher_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('main.teacher_dashboard'))
    
    # Get all attendance records for this course
    records = Attendance.query.filter_by(course_id=course_id).order_by(Attendance.date.desc()).all()
    
    # Group by student
    student_data = {}
    for record in records:
        if record.student_id not in student_data:
            student_data[record.student_id] = {
                'student': record.student,
                'records': [],
                'total': 0,
                'present': 0
            }
        student_data[record.student_id]['records'].append(record)
        student_data[record.student_id]['total'] += 1
        if record.status == 'present':
            student_data[record.student_id]['present'] += 1
    
    # Calculate percentages
    for student_id in student_data:
        data = student_data[student_id]
        if data['total'] > 0:
            data['percentage'] = round((data['present'] / data['total']) * 100, 2)
        else:
            data['percentage'] = 0
    
    return render_template('view_course_attendance.html', 
                         course=course, 
                         student_data=student_data)
@bp.route('/teacher/export-attendance/<int:course_id>')
@login_required
def export_attendance(course_id):
    """Export attendance to Excel"""
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    
    if course.teacher_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('main.teacher_dashboard'))
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance Report"
    
    # Add title
    ws['A1'] = f"Attendance Report - {course.name}"
    ws['A1'].font = Font(size=16, bold=True)
    ws['A2'] = f"Course Code: {course.code}"
    ws['A3'] = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Headers
    headers = ['Student Name', 'Email', 'Total Classes', 'Present', 'Absent', 'Late', 'Attendance %', 'Status']
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=5, column=col)
        cell.value = header
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.alignment = Alignment(horizontal='center')
    
    # Get attendance data
    records = Attendance.query.filter_by(course_id=course_id).all()
    
    student_data = {}
    for record in records:
        if record.student_id not in student_data:
            student_data[record.student_id] = {
                'student': record.student,
                'total': 0,
                'present': 0,
                'absent': 0,
                'late': 0
            }
        student_data[record.student_id]['total'] += 1
        student_data[record.student_id][record.status] += 1
    
    # Add data
    row = 6
    for student_id, data in student_data.items():
        percentage = round((data['present'] / data['total']) * 100, 2) if data['total'] > 0 else 0
        status = 'Good' if percentage >= 75 else 'Low'
        
        ws.cell(row=row, column=1, value=data['student'].username)
        ws.cell(row=row, column=2, value=data['student'].email)
        ws.cell(row=row, column=3, value=data['total'])
        ws.cell(row=row, column=4, value=data['present'])
        ws.cell(row=row, column=5, value=data['absent'])
        ws.cell(row=row, column=6, value=data['late'])
        ws.cell(row=row, column=7, value=f"{percentage}%")
        ws.cell(row=row, column=8, value=status)
        
        # Color code status
        status_cell = ws.cell(row=row, column=8)
        if percentage >= 75:
            status_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        else:
            status_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        
        row += 1
    
    # Adjust column widths
    for col in range(1, 9):
        ws.column_dimensions[chr(64 + col)].width = 15
    
    # Save to BytesIO
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    # Send file
    filename = f"attendance_{course.code}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    @bp.route('/create-admin-emergency', methods=['GET'])
def create_admin_emergency():
    """Emergency route to create admin user"""
    from app.models import User
    
    try:
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            return "Admin already exists! Try logging in with username: admin, password: Admin@123"
        
        # Create admin
        admin = User(
            username='admin',
            email='admin@attendance-system.com',
            role='teacher',
            roll_no=None
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        
        return """
        <h1>✅ Admin User Created!</h1>
        <p>Username: <strong>admin</strong></p>
        <p>Password: <strong>Admin@123</strong></p>
        <a href="/login">Go to Login</a>
        """
    
    except Exception as e:
        return f"Error: {e}"
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )
