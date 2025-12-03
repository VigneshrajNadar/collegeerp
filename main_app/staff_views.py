import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import tempfile
from datetime import date, datetime
from xhtml2pdf import pisa
from io import BytesIO
from django.contrib.auth.decorators import login_required

# Try importing xhtml2pdf, but don't fail if it's not available
try:
    from xhtml2pdf import pisa
    PDF_GENERATION_AVAILABLE = True
except ImportError:
    PDF_GENERATION_AVAILABLE = False

from .forms import *
from .models import *
from . import forms, models

def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    total_students = Student.objects.filter(course=staff.course).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    subjects = Subject.objects.filter(staff=staff)
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name)
        attendance_list.append(attendance_count)
    context = {
        'page_title': 'Staff Panel - ' + str(staff.admin.first_name) + ' ' + str(staff.admin.last_name[0]) + '' + ' (' + str(staff.course) + ')',
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Take Attendance'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        subject_id = request.POST.get('subject')
        print(f"[DEBUG] get_students view called with subject_id: {subject_id}")
        
        if not subject_id:
            return JsonResponse({'error': 'Subject ID is required'}, status=400)

        # Get the subject and its related course
        subject = get_object_or_404(Subject, id=subject_id)
        course = subject.course
        print(f"[DEBUG] Found subject: {subject.name}")
        print(f"[DEBUG] Associated course: {course.name}")
        
        # Get all students in this course
        students = Student.objects.filter(
            course=course
        ).select_related('admin')
        
        print(f"[DEBUG] Found {students.count()} students in course {course.name}")
        
        # Format student data
        student_data = []
        for student in students:
            try:
                # Get student name and details
                admin = student.admin
                name = f"{admin.first_name} {admin.last_name}".strip()
                if not name:
                    name = admin.email.split('@')[0] if admin.email else f"Student {student.id}"
                
                data = {
                    'id': student.id,
                    'name': name,
                    'email': admin.email,
                    'course': course.name
                }
                student_data.append(data)
                print(f"[DEBUG] Added student: {name} (ID: {student.id}, Email: {admin.email})")
            except Exception as e:
                print(f"[DEBUG] Error processing student {student.id}: {str(e)}")
                continue
        
        if not student_data:
            return JsonResponse({
                'error': f'No students found for course {course.name}. Please assign students to this course.'
            }, status=404)
        
        print(f"[DEBUG] Returning {len(student_data)} students")
        return JsonResponse(student_data, safe=False)
        
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)
    except Exception as e:
        print(f"[DEBUG] Error in get_students: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def save_attendance(request):
    try:
        student_data = request.POST.get('student_data')
        date = request.POST.get('attendance_date')
        subject_id = request.POST.get('subject')
        
        if not all([student_data, date, subject_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required data'
            }, status=400)
            
        # Parse the student data
        students = json.loads(student_data)
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Get the session from the first student's course
        # This assumes all students in the same course have the same session
        if students:
            first_student = get_object_or_404(Student, id=students[0].get('student_id'))
            session = first_student.session
            if not session:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Student has no session assigned'
                }, status=400)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No students provided'
            }, status=400)
        
        # Create attendance record
        attendance = Attendance.objects.create(
            subject=subject,
            date=date,
            session=session
        )
        
        # Create attendance reports for each student
        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('student_id'))
            AttendanceReport.objects.create(
                student=student,
                attendance=attendance,
                status=student_dict.get('status')
            )
            
        return JsonResponse({
            'status': 'success',
            'message': 'Attendance saved successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid student data format'
        }, status=400)
    except Exception as e:
        print(f"[DEBUG] Error saving attendance: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error saving attendance: {str(e)}'
        }, status=500)


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Update Attendance'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        print(f"[DEBUG] Received attendance_date_id: {attendance_date_id}")
        
        if not attendance_date_id:
            return JsonResponse({'error': 'Attendance date ID is required'}, status=400)

        # Get the attendance record
        attendance = get_object_or_404(Attendance, id=attendance_date_id)
        print(f"[DEBUG] Found attendance record for date: {attendance.date}")
        
        # Get all attendance reports for this attendance record
        attendance_data = AttendanceReport.objects.filter(attendance=attendance)
        print(f"[DEBUG] Found {attendance_data.count()} attendance records")
        
        # Format the data
        student_data = []
        for record in attendance_data:
            student = record.student
            data = {
                "id": student.id,  # Use student.id instead of admin.id
                "name": f"{student.admin.first_name} {student.admin.last_name}",
                "status": record.status
            }
            student_data.append(data)
            print(f"[DEBUG] Added student: {data['name']} with status: {data['status']}")
        
        if not student_data:
            print("[DEBUG] No attendance records found")
            return JsonResponse({'error': 'No attendance records found'}, status=404)
            
        print(f"[DEBUG] Returning {len(student_data)} student records")
        return JsonResponse(student_data, safe=False, status=200)
        
    except Attendance.DoesNotExist:
        print(f"[DEBUG] Attendance record not found for ID: {attendance_date_id}")
        return JsonResponse({'error': 'Attendance record not found'}, status=404)
    except Exception as e:
        print(f"[DEBUG] Error in get_student_attendance: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    
    try:
        print(f"[DEBUG] Received update request - date: {date}, student_data: {student_data}")
        
        if not date or not student_data:
            return JsonResponse({'error': 'Missing required data'}, status=400)
            
        students = json.loads(student_data)
        attendance = get_object_or_404(Attendance, id=date)
        
        print(f"[DEBUG] Found attendance record for date: {attendance.date}")
        print(f"[DEBUG] Updating {len(students)} student records")
        
        updated_count = 0
        for student_dict in students:
            try:
                student = get_object_or_404(Student, id=student_dict.get('id'))
                attendance_report = get_object_or_404(
                    AttendanceReport, 
                    student=student, 
                    attendance=attendance
                )
                attendance_report.status = student_dict.get('status')
                attendance_report.save()
                updated_count += 1
                print(f"[DEBUG] Updated attendance for student {student.admin.email}: {student_dict.get('status')}")
            except Exception as e:
                print(f"[DEBUG] Error updating student {student_dict.get('id')}: {str(e)}")
                continue
        
        print(f"[DEBUG] Successfully updated {updated_count} records")
        return JsonResponse({
            'message': f'Successfully updated attendance for {updated_count} students',
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        print("[DEBUG] Invalid JSON data received")
        return JsonResponse({'error': 'Invalid student data format'}, status=400)
    except Attendance.DoesNotExist:
        print(f"[DEBUG] Attendance record not found for ID: {date}")
        return JsonResponse({'error': 'Attendance record not found'}, status=404)
    except Exception as e:
        print(f"[DEBUG] Error in update_attendance: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


@login_required(login_url='login_page')
def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff=staff)
    
    context = {
        'subjects': subjects,
        'page_title': 'Add Result'
    }
    return render(request, 'staff_template/staff_add_result.html', context)


@login_required(login_url='login_page')
def staff_save_result(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        # Get form data
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        internal_marks = float(request.POST.get('internal_marks', 0))
        external_marks = float(request.POST.get('external_marks', 0))
        practical_marks = float(request.POST.get('practical_marks', 0))
        total_marks = float(request.POST.get('total_marks', 0))
        grade = request.POST.get('grade')

        # Validate data
        if not all([subject_id, student_id, semester, academic_year]):
            return JsonResponse({
                'status': 'error',
                'message': 'All fields are required'
            }, status=400)

        # Get subject and student instances
        subject = get_object_or_404(Subject, id=subject_id)
        student = get_object_or_404(Student, id=student_id)

        # Check if result already exists
        result_exists = StudentResult.objects.filter(
            student=student,
            subject=subject,
            semester=semester,
            academic_year=academic_year
        ).exists()

        if result_exists:
            return JsonResponse({
                'status': 'error',
                'message': 'Result already exists for this student in this subject'
            }, status=400)

        # Create new result
        result = StudentResult.objects.create(
            student=student,
            subject=subject,
            semester=semester,
            academic_year=academic_year,
            internal_marks=internal_marks,
            external_marks=external_marks,
            practical_marks=practical_marks,
            total_marks=total_marks,
            grade=grade
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Result added successfully'
        })

    except Subject.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Subject not found'
        }, status=404)
    except Student.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Student not found'
        }, status=404)
    except ValueError as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Invalid data: {str(e)}'
        }, status=400)
    except Exception as e:
        print(f"Error saving result: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while saving the result'
        }, status=500)


@csrf_exempt
def fetch_student_result(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        
        print(f"[DEBUG] fetch_student_result called with subject_id: {subject_id}, student_id: {student_id}")
        
        if not all([subject_id, student_id]):
            return JsonResponse({'error': 'Subject and student IDs are required'}, status=400)
        
        # Get the result
        result = StudentResult.objects.filter(
            student_id=student_id,
            subject_id=subject_id
        ).first()
        
        if result:
            print(f"[DEBUG] Found result for student {student_id} in subject {subject_id}")
            data = {
                'semester': result.semester,
                'academic_year': result.academic_year,
                'internal_marks': result.internal_marks,
                'external_marks': result.external_marks,
                'practical_marks': result.practical_marks,
                'total_marks': result.total_marks,
                'grade': result.grade
            }
            return JsonResponse(data)
        else:
            print(f"[DEBUG] No result found for student {student_id} in subject {subject_id}")
            return JsonResponse({
                'error': 'No result found for this student in this subject'
            }, status=404)
            
    except Exception as e:
        print(f"[DEBUG] Error in fetch_student_result: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)

#library
def add_book(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']


        books = Book.objects.create(name=name, author=author, isbn=isbn, category=category )
        books.save()
        alert = True
        return render(request, "staff_template/add_book.html", {'alert':alert})
    context = {
        'page_title': "Add Book"
    }
    return render(request, "staff_template/add_book.html",context)

#issue book


def issue_book(request):
    form = forms.IssueBookForm()
    if request.method == "POST":
        form = forms.IssueBookForm(request.POST)
        if form.is_valid():
            obj = models.IssuedBook()
            obj.student_id = request.POST['name2']
            obj.isbn = request.POST['isbn2']
            obj.save()
            alert = True
            return render(request, "staff_template/issue_book.html", {'obj':obj, 'alert':alert})
    return render(request, "staff_template/issue_book.html", {'form':form})

def view_issued_book(request):
    issuedBooks = IssuedBook.objects.all()
    details = []
    for i in issuedBooks:
        days = (date.today()-i.issued_date)
        d=days.days
        fine=0
        if d>14:
            day=d-14
            fine=day*5
        books = list(models.Book.objects.filter(isbn=i.isbn))
        # students = list(models.Student.objects.filter(admin=i.admin))
        i=0
        for l in books:
            t=(books[i].name,books[i].isbn,issuedBooks[0].issued_date,issuedBooks[0].expiry_date,fine)
            i=i+1
            details.append(t)
    return render(request, "staff_template/view_issued_book.html", {'issuedBooks':issuedBooks, 'details':details})

def generate_result(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        
        subject = get_object_or_404(Subject, id=subject_id)
        staff = get_object_or_404(Staff, admin=request.user)
        
        if subject.staff != staff:
            messages.error(request, "You don't have permission to generate results for this subject")
            return redirect('staff_home')
            
        # Use select_related to efficiently fetch related student and admin data
        results = StudentResult.objects.filter(
            subject=subject,
            semester=semester,
            academic_year=academic_year
        ).select_related(
            'student',
            'student__admin'
        ).order_by('student__admin__email')  # Order by email (roll number)
        
        if not results.exists():
            messages.warning(request, f"No results found for {subject.name} in semester {semester}, {academic_year}")
            return redirect('staff_generate_result')
        
        context = {
            'subject': subject,
            'semester': semester,
            'academic_year': academic_year,
            'results': results,
            'today': datetime.now(),
            'page_title': f"Result Sheet - {subject.name}"
        }
        
        return render(request, 'main_app/staff/view_result_sheet.html', context)
    else:
        staff = get_object_or_404(Staff, admin=request.user)
        subjects = Subject.objects.filter(staff=staff)
        
        if not subjects.exists():
            messages.warning(request, "You don't have any subjects assigned to you")
            return redirect('staff_home')
            
        context = {
            'subjects': subjects,
            'page_title': 'Generate Result'
        }
        return render(request, 'main_app/staff/generate_result.html', context)

def download_result(request, subject_id, semester, academic_year):
    subject = get_object_or_404(Subject, id=subject_id)
    staff = get_object_or_404(Staff, admin=request.user)
    
    if subject.staff != staff:
        messages.error(request, "You don't have permission to download results for this subject")
        return redirect('staff_home')
        
    # Use select_related here as well for PDF generation
    results = StudentResult.objects.filter(
        subject=subject,
        semester=semester,
        academic_year=academic_year
    ).select_related(
        'student',
        'student__admin'
    ).order_by('student__admin__email')
    
    context = {
        'subject': subject,
        'semester': semester,
        'academic_year': academic_year,
        'results': results,
        'today': datetime.now(),
        'page_title': f"Result Sheet - {subject.name}"
    }
    
    if not PDF_GENERATION_AVAILABLE:
        messages.error(request, "PDF generation is not available. Please install xhtml2pdf.")
        return redirect('staff_generate_result')
    
    try:
        html_string = render_to_string('main_app/staff/result_sheet.html', context)
        
        # Create a BytesIO object to receive the PDF data
        buffer = BytesIO()
        
        # Create the PDF object, using the BytesIO object as its "file."
        pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), buffer)
        
        # Get the value of the BytesIO buffer and write it to the response
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="result_sheet_{subject.name}_{semester}_{academic_year}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect('staff_generate_result')

@csrf_exempt
def get_attendance_dates(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id) if session_id else None
        
        # Query attendance records
        query = Attendance.objects.filter(subject=subject)
        if session:
            query = query.filter(session=session)
            
        # Order by date descending to show most recent first
        attendance_dates = query.order_by('-date')
        
        attendance_data = []
        for attendance in attendance_dates:
            data = {
                "id": attendance.id,
                "date": attendance.date.strftime('%Y-%m-%d')
            }
            attendance_data.append(data)
            
        return JsonResponse(attendance_data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)