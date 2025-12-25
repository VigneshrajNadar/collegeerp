# 🎓 College ERP System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> A comprehensive, modern, and user-friendly Enterprise Resource Planning (ERP) system tailored for educational institutions. Streamline your academic and administrative processes with ease.

---


## 🎯 Objectives

 Automate college administrative and academic processes
 Reduce paperwork and manual errors
 Provide centralized and secure data access
 Enable role-based dashboards for students, staff, and administrators
 Improve efficiency in attendance, exams, and result processing

---

## ✨ Key Features

### 🔐 Authentication & Security

 
 Secure login system 
 
 Role-based access control (Student / Staff / Admin)
 
 Data protection and access validation

---

## 👨‍🎓 Student Module

 
 Student dashboard with analytics
 
 View attendance (subject-wise & percentage)
 
 View examination results
 
 Download hall tickets
 
 Apply for leave
 
 Apply for KT (Keep Term)
 
 Apply for revaluation
 
 Track KT & revaluation status
 
 View notifications and announcements
 
 Submit feedback

 Student Help Chatbot
 
 Profile management

---


## 👨‍🏫 Staff Module

 
 Staff dashboard with performance metrics
 
 Take and update student attendance
 
 Add and edit results
 
 Generate final results
 
 Apply for leave
 
 Manage KT applications
 
 Handle revaluation requests
 
 View notifications
 
 Submit feedback
 
 Profile management

---



## 🛠 Admin Module

 
 Administrative dashboard with analytics
 
 Add / manage students, staff, courses, subjects, and sessions
 
 View and manage attendance records
 
 Manage examinations and exam halls
 
 Process KT and revaluation applications
 
 View student and staff feedback
 
 Send notifications to students and staff
 
 Monitor institutional statistics using charts

---


## 📊 Dashboards & Analytics


 Attendance analytics (charts & graphs)
 
 Subject-wise attendance visualization
 
 Student vs staff distribution
 
 Course and subject enrollment statistics
 
 Leave and attendance overview

---



## 🤖 Student Help Chatbot 

The Student Help Chatbot is an intelligent, interactive support feature designed to assist students with common academic and administrative queries in real time.

---

### 🔹 Purpose

To reduce dependency on manual help desks and provide instant, 24/7 assistance to students for routine college-related questions.

---

## ✨ Chatbot Features

 Answers frequently asked questions related to:

   Attendance
  
   Results
   
   Exams & hall tickets
   
   KT (Keep Term) applications
   
   Revaluation process
   
   Leave applications
   
   Notifications & announcements
 
 Provides step-by-step guidance for using system features
 
 Helps students navigate different modules of the CMS
 
 Reduces workload on administrative staff
 
 Fast and user-friendly conversational interface

---

## 🧠 Chatbot Functionality

 
 Rule-based / keyword-based response system
 
 Integrated within the Student Dashboard
 
 Context-aware responses based on selected queries
 
 Secure access (available only to authenticated students)

---



## 🗄 Database Design (Core Tables)


 Users
 
 Students
 
 Staff
 
 Courses
 
 Subjects
 
 Attendance
 
 Exams
 
 Results
 
 Leave Applications
 
 KT Applications
 
 Revaluation Requests
 
 Notifications

---



## 🛠️ Technology Stack

*   **Backend**: Python, Django
*   **Frontend**: HTML5, CSS3, JavaScript, Bootstrap, AdminLTE
*   **Database**: SQLite (Development), PostgreSQL (Production)
*   **PDF Generation**: xhtml2pdf


---

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites
*   Python 3.10 or higher installed.
*   Git installed.

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/VigneshrajNadar/College-ERP.git
    cd College-ERP
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Apply Migrations**
    ```bash
    python manage.py migrate
    ```

5.  **Create Admin User**
    ```bash
    python manage.py createsuperuser
    ```
    *Or use the shell to create one programmatically if needed.*

6.  **Run the Server**
    ```bash
    python manage.py runserver
    ```
    Access the app at `http://127.0.0.1:8000/`.

---

## 🔐 Default Credentials

Use these credentials to log in and test the system.

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@example.com` | `admin123` |
| **Staff** | *(Create via Admin)* | *(Set by Admin)* |
| **Student** | *(Create via Admin)* | *(Set by Admin)* |

---

## 📂 Project Structure

```
College-ERP/
├── college_management_system/  # Project settings & configuration
├── main_app/                   # Core application logic
│   ├── models.py              # Database schemas
│   ├── views.py               # Business logic
│   ├── urls.py                # Route definitions
│   ├── templates/             # HTML templates
│   └── static/                # CSS, JS, Images
├── media/                      # User uploaded content
├── requirements.txt            # Python dependencies
└── manage.py                   # Django management script
```


