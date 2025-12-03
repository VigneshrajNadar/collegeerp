from django.core.management.base import BaseCommand
from main_app.models import ChatBot

class Command(BaseCommand):
    help = 'Seeds the chatbot with initial questions and answers'

    def handle(self, *args, **kwargs):
        # Clear existing chatbot data
        ChatBot.objects.all().delete()

        # Define questions and answers
        chatbot_data = [
            # Academic Questions
            {
                'question': 'How do I calculate my CGPA?',
                'answer': 'Your CGPA is calculated as follows:\n1. Multiply each subject\'s grade point by its credit hours\n2. Add all these products together\n3. Divide the sum by total credit hours\n\nFor example:\n- Subject 1: Grade A (10) × 4 credits = 40\n- Subject 2: Grade B (8) × 3 credits = 24\n- Total credits = 7\n- CGPA = (40 + 24) ÷ 7 = 9.14\n\nYou can view your detailed CGPA calculation in the Results section of your portal.',
                'category': 'academic'
            },
            {
                'question': 'What is my CGPA?',
                'answer': 'To check your CGPA:\n1. Log into your student portal\n2. Go to the Results section\n3. Select your current semester\n4. Your CGPA will be displayed at the top\n\nIf you need help calculating your CGPA, ask "How do I calculate my CGPA?"',
                'category': 'academic'
            },
            {
                'question': 'What is the difference between KT and ATKT?',
                'answer': 'KT (Keep Term) and ATKT (Allowed To Keep Term) have different implications:\n\nKT:\n- You can attend the next semester while clearing backlogs\n- Maximum 2 subjects can be kept as KT\n- Must clear within 2 semesters\n\nATKT:\n- You cannot attend the next semester\n- Must clear all subjects before proceeding\n- Usually applies when failing in more than 2 subjects\n\nFor both cases, you need to apply through the portal and pay the required fees.',
                'category': 'academic'
            },
            {
                'question': 'What is KT?',
                'answer': 'KT (Keep Term) means you can attend the next semester while clearing backlogs. Maximum 2 subjects can be kept as KT and must be cleared within 2 semesters. You need to apply through the portal and pay the required fees.',
                'category': 'academic'
            },
            {
                'question': 'What is ATKT?',
                'answer': 'ATKT (Allowed To Keep Term) means you cannot attend the next semester. You must clear all subjects before proceeding. This usually applies when failing in more than 2 subjects. You need to apply through the portal and pay the required fees.',
                'category': 'academic'
            },
            {
                'question': 'How does the internal assessment system work?',
                'answer': 'The internal assessment system is structured as follows:\n\n1. Continuous Assessment (40%):\n   - Class participation (10%)\n   - Assignments (15%)\n   - Quiz scores (15%)\n\n2. Mid-term Examination (30%):\n   - Written test (20%)\n   - Practical/Viva (10%)\n\n3. End-term Examination (30%):\n   - Written test (20%)\n   - Project/Presentation (10%)\n\nEach component\'s marks are updated in real-time in your portal under the Internal Assessment section.',
                'category': 'academic'
            },
            {
                'question': 'What is internal assessment?',
                'answer': 'Internal assessment is 40% of your total marks, including:\n- Class participation (10%)\n- Assignments (15%)\n- Quiz scores (15%)\n\nAsk "How does the internal assessment system work?" for complete details.',
                'category': 'academic'
            },
            {
                'question': 'How do I check my attendance?',
                'answer': 'To check your attendance:\n1. Log into your student portal\n2. Go to the Attendance section\n3. Select your current semester\n4. View subject-wise attendance percentage\n\nMinimum attendance required is 75% for each subject.',
                'category': 'academic'
            },
            {
                'question': 'What is the minimum attendance required?',
                'answer': 'The minimum attendance required is 75% for each subject. If your attendance falls below this, you may need to apply for condonation or face consequences.',
                'category': 'academic'
            },
            {
                'question': 'How do I apply for leave?',
                'answer': 'To apply for leave:\n1. Log into your student portal\n2. Go to the Leave Application section\n3. Fill in the required details:\n   - Start date\n   - End date\n   - Reason for leave\n   - Supporting documents\n4. Submit for faculty approval\n\nYour application will be reviewed by your faculty advisor.',
                'category': 'academic'
            },

            # Library Questions
            {
                'question': 'What are the library rules and regulations?',
                'answer': 'Library Rules and Regulations:\n\n1. Membership:\n   - Valid college ID required\n   - Registration fee: ₹500 (refundable)\n   - Valid for entire course duration\n\n2. Borrowing Rules:\n   - Maximum 2 books at a time\n   - Loan period: 14 days\n   - Renewal allowed once if not reserved\n   - Reference books: In-library use only\n\n3. Fines:\n   - Late return: ₹5 per day\n   - Lost book: Cost of book + ₹500\n   - Damaged book: Repair cost or replacement\n\n4. General Rules:\n   - Silence must be maintained\n   - No food or drinks allowed\n   - Mobile phones must be on silent\n   - Bags must be kept in lockers',
                'category': 'library'
            },
            {
                'question': 'What are library timings?',
                'answer': 'Library Timings:\n- Monday to Friday: 9:00 AM to 8:00 PM\n- Saturday: 9:00 AM to 5:00 PM\n- Sunday: Closed\n- Holidays: Closed\n\nExtended hours during exam period: 8:00 AM to 10:00 PM',
                'category': 'library'
            },
            {
                'question': 'How many books can I borrow?',
                'answer': 'You can borrow up to 2 books at a time for a period of 14 days. Books can be renewed once if not reserved by others. Ask "What are the library rules and regulations?" for complete details.',
                'category': 'library'
            },
            {
                'question': 'What is the fine for late book return?',
                'answer': 'The fine for late book return is ₹5 per day after the due date. Maximum fine is capped at ₹500 per book. For lost books, you need to pay the cost of the book plus ₹500 fine.',
                'category': 'library'
            },

            # Exam Related Questions
            {
                'question': 'What is the complete exam preparation guide?',
                'answer': 'Complete Exam Preparation Guide:\n\n1. Before Exams:\n   - Download hall ticket 1 week before\n   - Check exam schedule and venue\n   - Prepare required documents:\n     * Hall ticket\n     * College ID\n     * Aadhar card\n     * Stationery\n\n2. During Exams:\n   - Arrive 30 minutes early\n   - Follow seating arrangement\n   - Read instructions carefully\n   - Manage time effectively\n\n3. After Exams:\n   - Results announced in 30 days\n   - Apply for revaluation within 15 days\n   - Download mark sheet after 45 days\n\n4. Important Dates:\n   - Hall ticket: 7 days before exam\n   - Results: 30 days after exam\n   - Revaluation: 15 days after results\n   - Mark sheet: 45 days after results',
                'category': 'exams'
            },
            {
                'question': 'How do I get my hall ticket?',
                'answer': 'To get your hall ticket:\n1. Log into your student portal\n2. Go to the Hall Tickets section\n3. Select your current semester\n4. Download and print your hall ticket\n\nHall tickets are available 7 days before the exam date.',
                'category': 'exams'
            },
            {
                'question': 'What documents do I need for exams?',
                'answer': 'Required documents for exams:\n- Hall ticket\n- College ID card\n- Aadhar card\n- Stationery (pens, pencils)\n- Calculator (if allowed)\n- Water bottle (transparent)\n\nAsk "What is the complete exam preparation guide?" for more details.',
                'category': 'exams'
            },
            {
                'question': 'How does the grading system work?',
                'answer': 'Grading System:\n\n1. Grade Points:\n   - O (Outstanding): 10 points\n   - A+ (Excellent): 9 points\n   - A (Very Good): 8 points\n   - B+ (Good): 7 points\n   - B (Above Average): 6 points\n   - C (Average): 5 points\n   - D (Pass): 4 points\n   - F (Fail): 0 points\n\n2. Passing Criteria:\n   - Minimum 40% in each subject\n   - 75% attendance required\n   - Internal + External marks\n\n3. Backlog System:\n   - Maximum 2 subjects for KT\n   - Must clear within 2 semesters\n   - Additional fees for re-examination\n\n4. Improvement:\n   - Can improve grades in next semester\n   - Best grade will be considered\n   - Maximum 2 subjects can be improved',
                'category': 'exams'
            },

            # Fee Related Questions
            {
                'question': 'What is the complete fee structure and payment process?',
                'answer': 'Complete Fee Structure and Payment Process:\n\n1. Fee Components:\n   - Tuition Fee: ₹25,000 per semester\n   - Library Fee: ₹2,000 per year\n   - Laboratory Fee: ₹3,000 per semester\n   - Development Fee: ₹5,000 per year\n   - Exam Fee: ₹1,500 per subject\n\n2. Payment Methods:\n   - Online Payment:\n     * Credit/Debit Card\n     * Net Banking\n     * UPI\n   - Offline Payment:\n     * Cash at college office\n     * Bank transfer\n     * Demand draft\n\n3. Payment Schedule:\n   - First installment: Before registration\n   - Second installment: Mid-semester\n   - Late payment: 5% fine per month\n\n4. Refund Policy:\n   - 100% refund: Before classes start\n   - 75% refund: Within 15 days\n   - 50% refund: Within 30 days\n   - No refund: After 30 days',
                'category': 'fees'
            },
            {
                'question': 'How do I pay my fees?',
                'answer': 'To pay your fees:\n1. Log into your student portal\n2. Go to the Fees section\n3. Select payment method:\n   - Online: Credit/Debit Card, Net Banking, UPI\n   - Offline: Cash, Bank transfer, Demand draft\n4. Complete the payment process\n5. Download the receipt\n\nAsk "What is the complete fee structure and payment process?" for detailed information.',
                'category': 'fees'
            },
            {
                'question': 'What is the fee structure?',
                'answer': 'Fee Structure:\n- Tuition Fee: ₹25,000 per semester\n- Library Fee: ₹2,000 per year\n- Laboratory Fee: ₹3,000 per semester\n- Development Fee: ₹5,000 per year\n- Exam Fee: ₹1,500 per subject\n\nAsk "What is the complete fee structure and payment process?" for complete details.',
                'category': 'fees'
            },
            {
                'question': 'How do I get a fee receipt?',
                'answer': 'To get your fee receipt:\n1. Log into your student portal\n2. Go to the Fees section\n3. Click on "Download Receipt"\n4. Select the payment date\n5. Download and print the receipt\n\nKeep this receipt for future reference.',
                'category': 'fees'
            },

            # Hostel Questions
            {
                'question': 'What are the complete hostel facilities and rules?',
                'answer': 'Complete Hostel Facilities and Rules:\n\n1. Accommodation:\n   - Single rooms (limited)\n   - Double rooms (standard)\n   - Triple rooms (economy)\n   - AC and non-AC options\n\n2. Facilities:\n   - 24/7 Wi-Fi\n   - Laundry service\n   - Common room with TV\n   - Study room\n   - Indoor games\n   - Gymnasium\n   - Medical room\n\n3. Rules and Regulations:\n   - Entry/Exit timings:\n     * Morning: 5:00 AM\n     * Evening: 10:00 PM\n   - Visitors allowed: 2:00 PM - 8:00 PM\n   - Curfew: 10:00 PM\n   - Room inspection: Weekly\n\n4. Mess Facilities:\n   - Three meals daily\n   - Special diet options\n   - Monthly menu rotation\n   - Food committee representation',
                'category': 'hostel'
            },
            {
                'question': 'How do I apply for hostel?',
                'answer': 'To apply for hostel:\n1. Log into your student portal\n2. Go to the Hostel section\n3. Fill the application form with:\n   - Personal details\n   - Address proof\n   - Medical certificate\n   - Parent\'s consent letter\n   - Recent photograph\n   - ID proof\n4. Submit the application\n\nAsk "How do I apply for hostel accommodation?" for complete details.',
                'category': 'hostel'
            },
            {
                'question': 'What are the hostel timings?',
                'answer': 'Hostel Timings:\n- Entry/Exit:\n  * Morning: 5:00 AM\n  * Evening: 10:00 PM\n- Visitors allowed: 2:00 PM - 8:00 PM\n- Curfew: 10:00 PM\n- Mess timings:\n  * Breakfast: 7:00 AM - 9:00 AM\n  * Lunch: 12:00 PM - 2:00 PM\n  * Dinner: 7:00 PM - 9:00 PM',
                'category': 'hostel'
            },
            {
                'question': 'What facilities are available in the hostel?',
                'answer': 'Hostel Facilities:\n- 24/7 Wi-Fi\n- Laundry service\n- Common room with TV\n- Study room\n- Indoor games\n- Gymnasium\n- Medical room\n- Mess with three meals daily\n- Special diet options\n- Monthly menu rotation\n\nAsk "What are the complete hostel facilities and rules?" for more details.',
                'category': 'hostel'
            },

            # Technical Questions
            {
                'question': 'How do I use the student portal effectively?',
                'answer': 'Student Portal Usage Guide:\n\n1. Login and Security:\n   - Use college email\n   - Change password monthly\n   - Enable 2FA for security\n   - Keep recovery email updated\n\n2. Main Features:\n   - Attendance tracking\n   - Result viewing\n   - Fee payment\n   - Leave application\n   - Library access\n   - Assignment submission\n\n3. Important Sections:\n   - Academic calendar\n   - Exam schedule\n   - Course materials\n   - Faculty contact\n   - Event calendar\n\n4. Mobile Access:\n   - Download college app\n   - Enable notifications\n   - Offline access available\n   - Quick actions menu',
                'category': 'technical'
            },
            {
                'question': 'How do I reset my password?',
                'answer': 'To reset your password:\n1. Go to the login page\n2. Click "Forgot Password"\n3. Enter your registered email\n4. Check your email for reset link\n5. Click the link and set new password\n\nIf you don\'t receive the email, contact IT support.',
                'category': 'technical'
            },
            {
                'question': 'How do I access the student portal?',
                'answer': 'To access the student portal:\n1. Go to portal.college.edu\n2. Enter your college email\n3. Enter your password\n4. Click Login\n\nIf you have trouble logging in:\n- Check your internet connection\n- Clear browser cache\n- Try a different browser\n- Contact IT support if issues persist',
                'category': 'technical'
            },
            {
                'question': 'What should I do if the portal is not working?',
                'answer': 'If the portal is not working:\n1. Try these solutions:\n   - Clear browser cache\n   - Use a different browser\n   - Check internet connection\n   - Try after 5 minutes\n\n2. If still not working:\n   - Contact IT support:\n     * Email: support@college.edu\n     * Phone: +1234567890\n     * Help desk: Room 101\n\n3. Emergency support available 24/7',
                'category': 'technical'
            },

            # General Questions
            {
                'question': 'How do I contact support?',
                'answer': 'You can contact support through:\n\n1. IT Support:\n   - Email: support@college.edu\n   - Phone: +1234567890\n   - Help desk: Room 101\n   - WhatsApp: +1234567890\n\n2. Academic Support:\n   - Visit your department office\n   - Contact your faculty advisor\n   - Email: academic@college.edu\n\n3. Emergency Support:\n   - Available 24/7\n   - Emergency number: +1234567890',
                'category': 'general'
            },
            {
                'question': 'How do I update my profile?',
                'answer': 'To update your profile:\n1. Log into your student portal\n2. Go to Profile section\n3. Click "Edit Profile"\n4. Update information:\n   - Personal details\n   - Contact information\n   - Profile picture\n   - Address\n5. Save changes\n\nNote: Some fields may require admin approval.',
                'category': 'general'
            },
            {
                'question': 'How do I get my ID card?',
                'answer': 'To get your ID card:\n1. New Students:\n   - ID cards issued at orientation\n   - Submit photo and documents\n   - Collect from Student Affairs office\n\n2. Replacement:\n   - Visit Student Affairs office\n   - Submit written application\n   - Pay replacement fee: ₹500\n   - Collect new ID card\n\n3. Lost ID Card:\n   - Report to security office\n   - Apply for replacement\n   - Pay replacement fee',
                'category': 'general'
            }
        ]

        # Create chatbot entries
        for data in chatbot_data:
            ChatBot.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Successfully seeded chatbot data')) 