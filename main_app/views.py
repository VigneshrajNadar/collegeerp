import json
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
import re
from django.template.loader import render_to_string
import tempfile
from io import BytesIO
try:
    from xhtml2pdf import pisa
except (ImportError, OSError):
    pisa = None

PDF_GENERATION_AVAILABLE = pisa is not None
import os


def is_staff(user):
    return user.user_type == '2'

def is_admin(user):
    return user.user_type == '1'

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject, ExamHall, Exam, HallTicket, Course, ExamSubject, KTApplication, RevaluationApplication, Notification, StudentResult, Student, ChatBot, AttendanceReport
from .utils import generate_hall_tickets_for_exam

# Create your views here.


def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))
    return render(request, 'main_app/login.html')


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")
    else:

        
        #Authenticate
        email = request.POST.get('email').lower() if request.POST.get('email') else None
        password = request.POST.get('password')
        print(f"DEBUG: Attempting login for email: {email}")
        
        user = EmailBackend.authenticate(request, username=email, password=password)
        if user != None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            # Debug why it failed
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(email=email).exists():
                print(f"DEBUG: Login failed - User with email {email} does not exist.")
            else:
                u = User.objects.get(email=email)
                if not u.check_password(password):
                    print(f"DEBUG: Login failed - Password incorrect for {email}.")
                else:
                    print(f"DEBUG: Login failed - Unknown reason for {email}.")
            
            messages.error(request, "Invalid details")
            return redirect("/")



def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        
        # Get attendance records for this subject and session
        attendance_records = Attendance.objects.filter(
            subject=subject,
            session=session
        ).order_by('-date')  # Most recent first
        
        attendance_list = []
        for attendance in attendance_records:
            data = {
                "id": attendance.id,
                "attendance_date": attendance.date.strftime('%Y-%m-%d'),  # Format date as YYYY-MM-DD
                "subject": attendance.subject.name,
                "session": str(attendance.session)
                    }
            attendance_list.append(data)
        
        return JsonResponse(attendance_list, safe=False)
    except Subject.DoesNotExist:
        print(f"Subject with ID {subject_id} not found")
        return JsonResponse({'error': 'Subject not found'}, status=404)
    except Session.DoesNotExist:
        print(f"Session with ID {session_id} not found")
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        print(f"Error in get_attendance: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """
    return HttpResponse(data, content_type='application/javascript')

def manage_exam_halls(request):
    """View for managing exam halls"""
    if request.user.user_type != '1':  # Only HOD can access
        return redirect('login_page')
    
    halls = ExamHall.objects.all()
    context = {
        'halls': halls
    }
    return render(request, 'main_app/hod/manage_exam_halls.html', context)

def add_exam_hall(request):
    """View for adding new exam hall"""
    if request.user.user_type != '1':  # Only HOD can access
        return redirect('login_page')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        capacity = request.POST.get('capacity')
        rows = request.POST.get('rows')
        columns = request.POST.get('columns')
        
        ExamHall.objects.create(
            name=name,
            capacity=capacity,
            rows=rows,
            columns=columns
        )
        messages.success(request, 'Exam hall added successfully')
        return redirect('manage_exam_halls')
    
    return render(request, 'main_app/hod/add_exam_hall.html')

def manage_exams(request):
    """View for managing exams"""
    if request.user.user_type != '1':  # Only HOD can access
        return redirect('login_page')
    
    exams = Exam.objects.all()
    context = {
        'exams': exams
    }
    return render(request, 'main_app/hod/manage_exams.html', context)

@login_required
def add_exam(request):
    if request.user.user_type != '1':
        return redirect(reverse('admin_home'))
    
    if request.method == 'POST':
        exam_name = request.POST.get('name')
        course_id = request.POST.get('course')
        hall_id = request.POST.get('hall')
        
        # Get arrays of subjects and their schedules
        subject_ids = request.POST.getlist('subjects[]')
        dates = request.POST.getlist('dates[]')
        start_times = request.POST.getlist('start_times[]')
        end_times = request.POST.getlist('end_times[]')
        
        try:
            course = Course.objects.get(id=course_id)
            hall = ExamHall.objects.get(id=hall_id)
            
            # Create the exam
            exam = Exam.objects.create(
                name=exam_name,
                course=course,
                hall=hall
            )
            
            # Create ExamSubject entries for each subject with its schedule
            for i in range(len(subject_ids)):
                subject = Subject.objects.get(id=subject_ids[i])
                ExamSubject.objects.create(
                    exam=exam,
                    subject=subject,
                    date=dates[i],
                    start_time=start_times[i],
                    end_time=end_times[i]
                )
            
            messages.success(request, 'Exam added successfully!')
            return redirect('manage_exams')
            
        except Exception as e:
            messages.error(request, f'Error adding exam: {str(e)}')
            return redirect('add_exam')
    
    context = {
        'page_title': 'Add Exam',
        'courses': Course.objects.all(),
        'subjects': Subject.objects.all(),
        'halls': ExamHall.objects.all(),
        'today': datetime.now().date()
    }
    return render(request, 'main_app/hod/add_exam.html', context)

def generate_hall_tickets(request, exam_id):
    """View for generating hall tickets for an exam"""
    if request.user.user_type != '1':  # Only HOD can access
        return redirect('login_page')
    
    try:
        tickets = generate_hall_tickets_for_exam(exam_id)
        messages.success(request, f'Successfully generated {len(tickets)} hall tickets')
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('manage_exams')

def view_hall_tickets(request, exam_id):
    """View for viewing hall tickets of an exam"""
    if request.user.user_type != '1':  # Only HOD can access
        return redirect('login_page')
    
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        tickets = HallTicket.objects.filter(exam=exam)
        context = {
            'exam': exam,
            'tickets': tickets
        }
        return render(request, 'main_app/hod/view_hall_tickets.html', context)
    except Exception as e:
        messages.error(request, f"Error loading hall tickets: {str(e)}")
        return redirect('manage_exams')

def student_hall_ticket(request):
    """View for students to view their hall ticket"""
    if request.user.user_type != '3':  # Only students can access
        return redirect('login_page')
    
    try:
        student = request.user.student
        tickets = HallTicket.objects.filter(student=student)
        context = {
            'tickets': tickets
        }
        return render(request, 'main_app/student/hall_ticket.html', context)
    except Exception as e:
        messages.error(request, f"Error loading hall tickets: {str(e)}")
        return redirect('student_home')

@login_required(login_url='login')
def student_apply_kt(request):
    student = get_object_or_404(Student, admin=request.user)
    
    # Get all subjects for the student's course
    subjects = Subject.objects.filter(course=student.course_id)
    
    # Get failed subjects (where grade is 'F')
    failed_subjects = []
    for subject in subjects:
        result = StudentResult.objects.filter(
            student=student,
            subject=subject
        ).first()
        if result and result.grade == 'F':
            failed_subjects.append(subject)
    
    # Get existing KT applications
    existing_applications = KTApplication.objects.filter(student=student)
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Check if application already exists
        if KTApplication.objects.filter(student=student, subject=subject).exists():
            messages.error(request, f"You have already applied for KT in {subject.name}")
            return redirect('student_apply_kt')
        
        # Create new application
        KTApplication.objects.create(
            student=student,
            subject=subject,
            status='pending'
        )
        messages.success(request, f"Successfully applied for KT in {subject.name}")
        return redirect('student_kt_applications')
    
    context = {
        'student': student,
        'subjects': subjects,
        'failed_subjects': failed_subjects,
        'existing_applications': existing_applications,
        'page_title': 'Apply for KT'
    }
    return render(request, 'student_template/apply_kt.html', context)

@login_required
def student_kt_applications(request):
    if request.user.user_type != '3':
        return redirect('login_page')
    
    student = request.user.student
    applications = KTApplication.objects.filter(student=student).order_by('-created_at')
    context = {
        'applications': applications,
        'page_title': 'My KT Applications'
    }
    return render(request, 'main_app/student/kt_applications.html', context)

@login_required(login_url='login')
def student_apply_revaluation(request):
    student = get_object_or_404(Student, admin=request.user)
    
    # Get all subjects for the student's course
    subjects = Subject.objects.filter(course=student.course_id)
    
    # Get all subjects that have results
    revaluation_subjects = []
    for subject in subjects:
        result = StudentResult.objects.filter(
            student=student,
            subject=subject
        ).first()
        if result:
            revaluation_subjects.append(subject)
    
    # Get existing revaluation applications
    existing_applications = RevaluationApplication.objects.filter(student=student)
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Check if application already exists
        if RevaluationApplication.objects.filter(student=student, subject=subject).exists():
            messages.error(request, f"You have already applied for revaluation in {subject.name}")
            return redirect('student_apply_revaluation')
        
        # Get the current result for the subject
        result = StudentResult.objects.get(student=student, subject=subject)
        
        # Create new application
        RevaluationApplication.objects.create(
            student=student,
            subject=subject,
            semester=result.semester,
            current_marks=result.internal_marks + result.external_marks + result.practical_marks,
            status='pending'
        )
        messages.success(request, f"Successfully applied for revaluation in {subject.name}")
        return redirect('student_revaluation_applications')
    
    context = {
        'student': student,
        'subjects': subjects,
        'revaluation_subjects': revaluation_subjects,
        'existing_applications': existing_applications,
        'page_title': 'Apply for Revaluation'
    }
    return render(request, 'student_template/apply_revaluation.html', context)

@login_required
def student_revaluation_applications(request):
    if request.user.user_type != '3':
        return redirect('login_page')
    
    student = request.user.student
    applications = RevaluationApplication.objects.filter(student=student).order_by('-created_at')
    context = {
        'applications': applications,
        'page_title': 'My Revaluation Applications'
    }
    return render(request, 'main_app/student/revaluation_applications.html', context)

@login_required(login_url='login')
@user_passes_test(is_staff)
def staff_manage_kt_applications(request):
    kt_applications = KTApplication.objects.all().order_by('-created_at')
    return render(request, 'main_app/staff/manage_kt_applications.html', {
        'kt_applications': kt_applications
    })

@login_required(login_url='login')
@user_passes_test(is_staff)
def staff_manage_revaluation_applications(request):
    revaluation_applications = RevaluationApplication.objects.all().order_by('-created_at')
    return render(request, 'main_app/staff/manage_revaluation_applications.html', {
        'revaluation_applications': revaluation_applications
    })

@login_required(login_url='login')
@user_passes_test(is_staff)
def staff_update_kt_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(KTApplication, id=application_id)
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        
        application.status = status
        application.remarks = remarks
        application.save()
        
        # Create notification for student
        Notification.objects.create(
            user=application.student.admin,
            title='KT Application Update',
            message=f'Your KT application for {application.subject.name} has been {status}. Remarks: {remarks}',
            notification_type='kt'
        )
        
        messages.success(request, 'KT application status updated successfully.')
    return redirect('staff_manage_kt_applications')

@login_required(login_url='login')
@user_passes_test(is_staff)
def staff_update_revaluation_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(RevaluationApplication, id=application_id)
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        
        application.status = status
        application.remarks = remarks
        application.save()
        
        if status == 'approved':
            try:
                # Get the marks from the form
                internal_marks = float(request.POST.get('internal_marks', 0))
                external_marks = float(request.POST.get('external_marks', 0))
                practical_marks = float(request.POST.get('practical_marks', 0))
                
                # Update the result
                result = StudentResult.objects.get(
                    student=application.student,
                    subject=application.subject,
                    semester=application.semester
                )
                
                result.internal_marks = internal_marks
                result.external_marks = external_marks
                result.practical_marks = practical_marks
                result.total_marks = internal_marks + external_marks + practical_marks
                
                # Calculate grade based on total marks
                total = result.total_marks
                if total >= 90:
                    result.grade = 'A+'
                elif total >= 80:
                    result.grade = 'A'
                elif total >= 70:
                    result.grade = 'B+'
                elif total >= 60:
                    result.grade = 'B'
                elif total >= 50:
                    result.grade = 'C'
                else:
                    result.grade = 'F'
                
                result.save()

                # Create notification for student
                Notification.objects.create(
                    user=application.student.admin,
                    title='Revaluation Result Update',
                    message=f'Your revaluation application for {application.subject.name} has been {status}. New total marks: {result.total_marks}. Grade: {result.grade}. Remarks: {remarks}',
                    notification_type='revaluation'
                )
            except Exception as e:
                messages.error(request, f'Error updating marks: {str(e)}')
                return redirect('staff_manage_revaluation_applications')
        else:
            # Create notification for rejected status
            Notification.objects.create(
                user=application.student.admin,
                title='Revaluation Application Update',
                message=f'Your revaluation application for {application.subject.name} has been {status}. Remarks: {remarks}',
                notification_type='revaluation'
            )
        
        messages.success(request, 'Revaluation application status updated successfully.')
        return redirect('staff_manage_revaluation_applications')
    
    return redirect('staff_manage_revaluation_applications')

# Admin views for KT and Revaluation management
@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_manage_kt_applications(request):
    kt_applications = KTApplication.objects.all().order_by('-created_at')
    return render(request, 'main_app/admin/manage_kt_applications.html', {
        'kt_applications': kt_applications
    })

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_manage_revaluation_applications(request):
    revaluation_applications = RevaluationApplication.objects.all().order_by('-created_at')
    return render(request, 'main_app/admin/manage_revaluation_applications.html', {
        'revaluation_applications': revaluation_applications
    })

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_update_kt_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(KTApplication, id=application_id)
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        
        application.status = status
        application.remarks = remarks
        application.save()
        
        # Create notification for student
        Notification.objects.create(
            user=application.student.admin,
            title='KT Application Update',
            message=f'Your KT application for {application.subject.name} has been {status}. Remarks: {remarks}',
            notification_type='kt'
        )
        
        messages.success(request, 'KT application status updated successfully.')
    return redirect('admin_manage_kt_applications')

@login_required(login_url='login')
@user_passes_test(is_admin)
def admin_update_revaluation_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(RevaluationApplication, id=application_id)
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        
        application.status = status
        application.remarks = remarks
        application.save()
        
        # Create notification for student
        Notification.objects.create(
            user=application.student.admin,
            title='Revaluation Application Update',
            message=f'Your revaluation application for {application.subject.name} has been {status}. Remarks: {remarks}',
            notification_type='revaluation'
        )
        
        messages.success(request, 'Revaluation application status updated successfully.')
    return redirect('admin_manage_revaluation_applications')

@login_required(login_url='login')
def student_notifications(request):
    if request.user.user_type != '3':
        return redirect('login_page')
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark notifications as read when viewed
    notifications.update(is_read=True)
    
    context = {
        'notifications': notifications,
        'page_title': 'My Notifications'
    }
    return render(request, 'main_app/student/notifications.html', context)

@csrf_exempt
def get_students(request):
    print("[DEBUG] get_students view called")
    
    if request.method != 'POST':
        print("[DEBUG] Invalid request method")
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        subject_id = request.POST.get('subject')
        print(f"[DEBUG] Received subject_id: {subject_id}")
        
        if not subject_id:
            print("[DEBUG] No subject_id provided")
            return JsonResponse({'error': 'Subject ID is required'}, status=400)
        
        # Get the subject and its associated course
        subject = Subject.objects.select_related('course', 'staff').get(id=subject_id)
        print(f"[DEBUG] Found subject: {subject.name}, Course: {subject.course.name}")
        
        # Get all students in this course
        students = Student.objects.filter(
            course_id=subject.course_id
        ).select_related('admin')
        print(f"[DEBUG] Found {students.count()} students in course")
        
        student_list = []
        for student in students:
            try:
                first_name = student.admin.first_name or ''
                last_name = student.admin.last_name or ''
                name = f"{first_name} {last_name}".strip()
                if not name:
                    name = student.admin.username
                
                student_data = {
                    'id': student.id,
                    'name': name,
                    'roll_number': student.admin.username
                }
                student_list.append(student_data)
                print(f"[DEBUG] Added student: {name} ({student.admin.username})")
            except Exception as e:
                print(f"[DEBUG] Error processing student {student.id}: {str(e)}")
                continue
        
        print(f"[DEBUG] Returning {len(student_list)} students")
        return JsonResponse(student_list, safe=False)
        
    except Subject.DoesNotExist:
        print(f"[DEBUG] Subject with ID {subject_id} not found")
        return JsonResponse({'error': 'Subject not found'}, status=404)
    except Exception as e:
        print(f"[DEBUG] Error in get_students: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def save_result(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        test_score = request.POST.get('test_score')
        exam_score = request.POST.get('exam_score')
        
        # Validate required fields
        if not all([subject_id, student_id, test_score, exam_score]):
            return JsonResponse({
                'status': 'error',
                'message': 'All fields are required'
            }, status=400)
            
        # Convert scores to float and validate range
        try:
            test_score = float(test_score)
            exam_score = float(exam_score)
            if not (0 <= test_score <= 100 and 0 <= exam_score <= 100):
                raise ValueError("Scores must be between 0 and 100")
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
        # Get or create student result
        student_result, created = StudentResult.objects.get_or_create(
            student_id=student_id,
            subject_id=subject_id,
            defaults={
                'test_score': test_score,
                'exam_score': exam_score
            }
        )
        
        if not created:
            # Update existing result
            student_result.test_score = test_score
            student_result.exam_score = exam_score
            student_result.save()
            
        return JsonResponse({
            'status': 'success',
            'message': 'Result saved successfully'
        })
        
    except Exception as e:
        print(f"[ERROR] Error saving result: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error saving result: {str(e)}'
        }, status=500)

@login_required
def add_result(request):
    if request.user.user_type != '2':  # Only staff can access
        return redirect('login_page')
        
    try:
        staff = request.user.staff
        # Get subjects taught by this staff member
        subjects = Subject.objects.filter(staff=staff).select_related('course')
        print(f"[DEBUG] Found {subjects.count()} subjects for staff")
        
        if not PDF_GENERATION_AVAILABLE:
            messages.error(request, "PDF generation is not available. Please install xhtml2pdf package.")
            return redirect('staff_home')
        
        context = {
            'page_title': 'Add Student Result',
            'subjects': subjects
        }
        return render(request, 'staff_template/add_result.html', context)
    except Exception as e:
        print(f"[DEBUG] Error in add_result: {str(e)}")
        messages.error(request, f"Error loading page: {str(e)}")
        return redirect('staff_home')

def chatbot_page(request):
    return render(request, 'main_app/chatbot.html')

def chatbot_query(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip().lower()
            
            # Get all chatbot entries
            all_entries = ChatBot.objects.all()
            
            # Initialize best match variables
            best_match = None
            best_score = 0
            
            # Enhanced keywords for different categories with synonyms
            category_keywords = {
                'academic': [
                    'cgpa', 'attendance', 'kt', 'atkt', 'leave', 'internal', 'grade', 'result',
                    'marks', 'score', 'study', 'exam', 'test', 'assignment', 'project', 'semester',
                    'course', 'subject', 'class', 'lecture', 'teacher', 'professor', 'faculty'
                ],
                'library': [
                    'book', 'library', 'borrow', 'fine', 'return', 'study', 'read', 'textbook',
                    'reference', 'journal', 'magazine', 'research', 'paper', 'publication',
                    'digital', 'online', 'database', 'catalog', 'shelf', 'librarian'
                ],
                'exams': [
                    'exam', 'hall ticket', 'grade', 'result', 'paper', 'question', 'test',
                    'midterm', 'final', 'semester', 'schedule', 'date', 'time', 'venue',
                    'room', 'hall', 'seat', 'admit card', 'marksheet', 'answer sheet'
                ],
                'fees': [
                    'fee', 'payment', 'money', 'pay', 'receipt', 'scholarship', 'tuition',
                    'cost', 'expense', 'charge', 'due', 'installment', 'refund', 'discount',
                    'concession', 'financial', 'bank', 'transaction', 'online payment'
                ],
                'hostel': [
                    'hostel', 'room', 'mess', 'food', 'stay', 'accommodation', 'boarding',
                    'lodging', 'residence', 'dormitory', 'meal', 'dining', 'laundry',
                    'facility', 'amenity', 'furniture', 'maintenance', 'security'
                ],
                'technical': [
                    'portal', 'password', 'login', 'access', 'website', 'app', 'system',
                    'computer', 'internet', 'network', 'email', 'account', 'profile',
                    'settings', 'update', 'download', 'upload', 'file', 'document'
                ],
                'general': [
                    'support', 'help', 'contact', 'profile', 'id card', 'document',
                    'information', 'guide', 'assistance', 'service', 'office', 'department',
                    'staff', 'admin', 'head', 'principal', 'campus', 'facility'
                ]
            }
            
            # Common greetings and farewells
            greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
            farewells = ['bye', 'goodbye', 'see you', 'thank you', 'thanks']
            
            # Check for greetings
            if any(greeting in query for greeting in greetings):
                return JsonResponse({
                    'status': 'success',
                    'answer': "Hello! I'm your college assistant. How can I help you today?",
                    'category': 'general'
                })
            
            # Check for farewells
            if any(farewell in query for farewell in farewells):
                return JsonResponse({
                    'status': 'success',
                    'answer': "Goodbye! Feel free to ask if you need any more help.",
                    'category': 'general'
                })
            
            # Function to calculate similarity score with enhanced matching
            def calculate_similarity(q1, q2):
                # Convert to sets for word matching
                words1 = set(q1.split())
                words2 = set(q2.split())
                
                # Calculate Jaccard similarity
                intersection = len(words1.intersection(words2))
                union = len(words1.union(words2))
                
                if union == 0:
                    return 0
                
                # Add bonus for exact phrase matches
                if q1 in q2 or q2 in q1:
                    return 1.0
                
                # Add bonus for word order similarity
                words1_list = q1.split()
                words2_list = q2.split()
                order_similarity = sum(1 for i in range(min(len(words1_list), len(words2_list)))
                                    if words1_list[i] == words2_list[i]) / max(len(words1_list), len(words2_list))
                
                return (intersection / union) + (order_similarity * 0.2)
            
            # Function to check if query contains category keywords with context
            def get_category_score(query, category):
                score = 0
                words = query.split()
                
                # Check for exact keyword matches
                for keyword in category_keywords.get(category, []):
                    if keyword in query:
                        score += 1
                
                # Check for related words and context
                for word in words:
                    for keyword in category_keywords.get(category, []):
                        if word in keyword or keyword in word:
                            score += 0.5
                
                return score
            
            # Find best match with context
            for entry in all_entries:
                # Calculate similarity with the question
                similarity = calculate_similarity(query, entry.question.lower())
                
                # Add category keyword bonus
                category_score = get_category_score(query, entry.category)
                similarity += (category_score * 0.1)  # Add 10% bonus for each matching keyword
                
                # Add context bonus for related words
                if any(word in query for word in entry.question.lower().split()):
                    similarity += 0.2
                
                # Update best match if this is better
                if similarity > best_score:
                    best_score = similarity
                    best_match = entry
            
            # If we have a good match (similarity > 0.3)
            if best_match and best_score > 0.3:
                response = best_match.answer
                
                # Add related questions based on category and context
                related_questions = ChatBot.objects.filter(
                    category=best_match.category
                ).exclude(id=best_match.id)[:3]
                
                if related_questions:
                    response += "\n\nRelated questions you might want to ask:\n"
                    for q in related_questions:
                        response += f"- {q.question}\n"
                
                # Add follow-up suggestions based on context
                if 'fee' in query or 'payment' in query:
                    response += "\nWould you like to know about:\n- How to pay fees online?\n- Fee structure details?\n- Scholarship opportunities?"
                elif 'exam' in query or 'test' in query:
                    response += "\nWould you like to know about:\n- Exam schedule?\n- Hall ticket download?\n- Result checking?"
                elif 'attendance' in query:
                    response += "\nWould you like to know about:\n- Minimum attendance requirements?\n- Leave application process?\n- Attendance calculation?"
                
                return JsonResponse({
                    'status': 'success',
                    'answer': response,
                    'category': best_match.category
                })
            else:
                # If no good match found, provide a contextual response
                # Try to identify the general topic
                topic_keywords = {
                    'academic': ['study', 'class', 'course', 'subject'],
                    'administrative': ['form', 'application', 'document', 'certificate'],
                    'facilities': ['campus', 'building', 'room', 'hall'],
                    'events': ['festival', 'program', 'competition', 'activity']
                }
                
                identified_topic = None
                for topic, keywords in topic_keywords.items():
                    if any(keyword in query for keyword in keywords):
                        identified_topic = topic
                        break
                
                if identified_topic:
                    response = f"I understand you're asking about {identified_topic} related matters. "
                else:
                    response = "I'm not sure about that. "
                
                response += "Here are some common questions you can ask:\n\n" + \
                           "1. How do I check my attendance?\n" + \
                           "2. What is the fee structure?\n" + \
                           "3. How do I apply for leave?\n" + \
                           "4. What are the library timings?\n" + \
                           "5. How do I get my hall ticket?\n\n" + \
                           "Try asking any of these questions or rephrase your question."
                
                return JsonResponse({
                    'status': 'success',
                    'answer': response,
                    'category': 'general'
                })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

def download_hall_ticket(request, ticket_id):
    try:
        ticket = HallTicket.objects.get(id=ticket_id)
        
        # Check if user is HOD or Staff
        if request.user.user_type in ['1', '2']:
            # HOD and Staff can download any hall ticket
            pass
        # Check if user is a student
        elif request.user.user_type == '3':
            try:
                student = request.user.student
                if ticket.student != student:
                    messages.error(request, "You don't have permission to download this hall ticket")
                    return redirect('student_hall_ticket')
            except Student.DoesNotExist:
                messages.error(request, "Student profile not found")
                return redirect('student_home')
        else:
            messages.error(request, "You don't have permission to download hall tickets")
            return redirect('login_page')
        
        # Render the hall ticket template
        context = {
            'ticket': ticket
        }
        
        if not PDF_GENERATION_AVAILABLE:
            messages.error(request, "PDF generation is not available. Please install xhtml2pdf.")
            return redirect('student_hall_ticket')

        html_string = render_to_string('main_app/student/hall_ticket_pdf.html', context)
        
        # Create PDF
        buffer = BytesIO()
        pisa_status = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), buffer)
        
        if pisa_status.err:
             messages.error(request, "Error generating PDF")
             return redirect('student_hall_ticket')
            
        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=hall_ticket_{ticket.hall_ticket_number}.pdf'
        return response
    except Exception as e:
        print(f"[DEBUG] Error generating hall ticket PDF: {str(e)}")
        messages.error(request, f"Error generating hall ticket: {str(e)}")
        return redirect('student_hall_ticket')

def delete_hall_ticket(request, ticket_id):
    """View for deleting a hall ticket"""
    if request.user.user_type != '1':  # Only HOD can delete
        messages.error(request, "You don't have permission to delete hall tickets")
        return redirect('login_page')
    
    try:
        ticket = get_object_or_404(HallTicket, id=ticket_id)
        exam_id = ticket.exam.id  # Store exam_id before deletion
        ticket.delete()
        messages.success(request, "Hall ticket deleted successfully")
        return redirect('view_hall_tickets', exam_id=exam_id)
    except Exception as e:
        messages.error(request, f"Error deleting hall ticket: {str(e)}")
        return redirect('manage_exams')

def delete_exam(request, exam_id):
    """View for deleting an exam"""
    if request.user.user_type != '1':  # Only HOD can delete
        messages.error(request, "You don't have permission to delete exams")
        return redirect('login_page')
    
    try:
        exam = get_object_or_404(Exam, id=exam_id)
        
        # Delete all associated hall tickets first
        HallTicket.objects.filter(exam=exam).delete()
        
        # Delete all exam subjects
        ExamSubject.objects.filter(exam=exam).delete()
        
        # Finally delete the exam
        exam.delete()
        
        messages.success(request, "Exam and all associated data deleted successfully")
        return redirect('manage_exams')
    except Exception as e:
        messages.error(request, f"Error deleting exam: {str(e)}")
        return redirect('manage_exams')

def staff_result(request):
    """View for staff to view and manage results"""
    if request.user.user_type != '2':  # Only staff can access
        return redirect('login_page')
    
    try:
        staff = request.user.staff
        subjects = Subject.objects.filter(staff=staff)
        semesters = ['1', '2', '3', '4', '5', '6', '7', '8']  # All 8 semesters
        academic_years = ['2023-24', '2024-25']  # Add more years as needed
        
        context = {
            'subjects': subjects,
            'semesters': semesters,
            'academic_years': academic_years
        }
        return render(request, 'main_app/staff/result.html', context)
    except Exception as e:
        messages.error(request, f"Error loading results: {str(e)}")
        return redirect('staff_home')

def student_view_result(request):
    """View for students to view their results"""
    if request.user.user_type != '3':  # Only students can access
        return redirect('login_page')
    
    try:
        student = request.user.student
        semesters = ['1', '2', '3', '4', '5', '6', '7', '8']  # Added semester 8
        academic_years = ['2023-24', '2024-25']  # Add more years as needed
        
        context = {
            'student': student,
            'semesters': semesters,
            'academic_years': academic_years
        }
        return render(request, 'main_app/student/view_result.html', context)
    except Exception as e:
        messages.error(request, f"Error loading results: {str(e)}")
        return redirect('student_home')

def student_download_result(request):
    """View for students to download their results"""
    if request.user.user_type != '3':  # Only students can access
        return redirect('login_page')
    
    try:
        student = request.user.student
        semester = request.GET.get('semester', '')
        academic_year = request.GET.get('academic_year', '')
        
        results = StudentResult.objects.filter(student=student)
        if semester and academic_year:
            results = results.filter(semester=semester, academic_year=academic_year)
        
        context = {
            'student': student,
            'results': results,
            'semester': semester,
            'academic_year': academic_year,
            'today': datetime.now()
        }
        
        if not PDF_GENERATION_AVAILABLE:
            messages.error(request, "PDF generation is not available. Please install xhtml2pdf package.")
            return redirect('student_view_result')
        
        html_string = render_to_string('main_app/student/result_pdf.html', context)
        
        # Create PDF
        buffer = BytesIO()
        pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), buffer)
        
        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="result_card_{student.admin.username}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect('student_view_result')

@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    print(f"[DEBUG] get_student_attendance called with attendance_date_id: {attendance_date_id}")

    try:
        # Get attendance record
        attendance = Attendance.objects.get(id=attendance_date_id)
        print(f"[DEBUG] Found attendance for subject: {attendance.subject.name}")

        # Get students for this subject's course
        students = Student.objects.filter(
            course_id=attendance.subject.course_id
        ).select_related('admin')
        print(f"[DEBUG] Found {students.count()} students")

        # Get attendance reports
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance
        ).values_list('student_id', 'status')
        attendance_dict = dict(attendance_reports)
        print(f"[DEBUG] Found {len(attendance_dict)} attendance records")

        student_list = []
        for student in students:
            try:
                name = f"{student.admin.first_name} {student.admin.last_name}".strip()
                if not name:
                    name = student.admin.username

                student_list.append({
                    'id': student.id,
                    'name': name,
                    'roll_number': student.admin.username,
                    'status': attendance_dict.get(student.id, False)
                })
                print(f"[DEBUG] Added student: {name}")
            except Exception as e:
                print(f"[DEBUG] Error processing student {student.id}: {str(e)}")
                continue

        print(f"[DEBUG] Returning {len(student_list)} students")
        return JsonResponse(student_list, safe=False)

    except Exception as e:
        print(f"[DEBUG] Error in get_student_attendance: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def update_attendance(request):
    try:
        student_data = request.POST.get('student_ids')
        date = request.POST.get('date')
        
        if not student_data or not date:
            return JsonResponse({'error': 'Missing required data'}, status=400)
            
        students = json.loads(student_data)
        attendance = get_object_or_404(Attendance, id=date)
        
        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))
            attendance_report = AttendanceReport.objects.filter(
                student=student, 
                attendance=attendance
            ).first()
            
            if attendance_report:
                attendance_report.status = student_dict.get('status')
                attendance_report.save()
            else:
                # Create new attendance report if it doesn't exist
                AttendanceReport.objects.create(
                    student=student,
                    attendance=attendance,
                    status=student_dict.get('status')
                )
                
        return HttpResponse("OK")
    except json.JSONDecodeError:
        print("Error: Invalid JSON data received")
        return JsonResponse({'error': 'Invalid data format'}, status=400)
    except Student.DoesNotExist:
        print("Error: Student not found")
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Attendance.DoesNotExist:
        print("Error: Attendance record not found")
        return JsonResponse({'error': 'Attendance record not found'}, status=404)
    except Exception as e:
        print(f"Error in update_attendance: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
