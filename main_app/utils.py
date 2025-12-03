from django.db import transaction
from .models import HallTicket, Exam, Student

def generate_seat_number(row, col):
    """Generate a seat number in the format ROW-COL"""
    return f"{row:02d}-{col:02d}"

def generate_bench_number(row):
    """Generate a bench number based on the row"""
    return f"B{row:02d}"

def allocate_seats(exam_id):
    """
    Automatically allocate seats and bench numbers to students for an exam.
    Returns a list of created HallTicket objects.
    """
    exam = Exam.objects.get(id=exam_id)
    hall = exam.hall
    
    # Get all students enrolled in the course
    students = Student.objects.filter(course=exam.course)
    
    created_tickets = []
    current_row = 1
    current_col = 1
    
    with transaction.atomic():
        for student in students:
            # Generate seat and bench numbers
            seat_number = generate_seat_number(current_row, current_col)
            bench_number = generate_bench_number(current_row)
            
            # Create hall ticket
            hall_ticket = HallTicket.objects.create(
                student=student,
                exam=exam,
                seat_number=seat_number,
                bench_number=bench_number
            )
            created_tickets.append(hall_ticket)
            
            # Update position for next student
            current_col += 1
            if current_col > hall.columns:
                current_col = 1
                current_row += 1
                
            # Check if we've exceeded hall capacity
            if current_row > hall.rows:
                raise ValueError("Hall capacity exceeded")
    
    return created_tickets

def generate_hall_tickets_for_exam(exam_id):
    """
    Generate hall tickets for all students in an exam.
    This function handles the entire process of hall ticket generation.
    """
    try:
        return allocate_seats(exam_id)
    except Exception as e:
        raise Exception(f"Failed to generate hall tickets: {str(e)}") 