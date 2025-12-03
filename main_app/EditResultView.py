from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Subject, Student, StudentResult

class EditResultView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        staff = request.user.staff
        subjects = Subject.objects.filter(staff=staff)
        context = {
            'subjects': subjects,
            'page_title': 'Edit Student Result'
        }
        return render(request, 'staff_template/edit_student_result.html', context)

    def post(self, request, *args, **kwargs):
        try:
            subject_id = request.POST.get('subject')
            student_id = request.POST.get('student')
            semester = request.POST.get('semester')
            academic_year = request.POST.get('academic_year')
            internal_marks = float(request.POST.get('internal_marks', 0))
            external_marks = float(request.POST.get('external_marks', 0))
            practical_marks = float(request.POST.get('practical_marks', 0))
            total_marks = float(request.POST.get('total_marks', 0))
            grade = request.POST.get('grade')

            # Validate required fields
            if not all([subject_id, student_id, semester, academic_year]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'All fields are required'
                }, status=400)

            # Get subject and student instances
            subject = get_object_or_404(Subject, id=subject_id)
            student = get_object_or_404(Student, id=student_id)

            # Check if staff is authorized to edit this subject's results
            if subject.staff != request.user.staff:
                return JsonResponse({
                    'status': 'error',
                    'message': 'You are not authorized to edit results for this subject'
                }, status=403)

            # Get or create result
            result, created = StudentResult.objects.get_or_create(
                student=student,
                subject=subject,
                semester=semester,
                academic_year=academic_year,
                defaults={
                    'internal_marks': internal_marks,
                    'external_marks': external_marks,
                    'practical_marks': practical_marks,
                    'total_marks': total_marks,
                    'grade': grade
                }
            )

            if not created:
                # Update existing result
                result.internal_marks = internal_marks
                result.external_marks = external_marks
                result.practical_marks = practical_marks
                result.total_marks = total_marks
                result.grade = grade
                result.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Result updated successfully'
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
            print(f"Error updating result: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred while updating the result'
            }, status=500)
