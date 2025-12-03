# 🎓 College ERP System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

> A comprehensive, modern, and user-friendly Enterprise Resource Planning (ERP) system tailored for educational institutions. Streamline your academic and administrative processes with ease.

---

## 📖 Overview

The **College ERP System** is designed to bridge the gap between students, staff, and administration. It provides a centralized platform to manage everything from student attendance and results to staff leave applications and exam scheduling. Built with **Django**, it ensures security, scalability, and a seamless user experience.

## ✨ Key Features

### 👨‍🎓 Student Module
*   **Profile Management**: View and update personal details.
*   **Academics**: Check subject-wise attendance and exam results.
*   **Applications**: Apply for leave, KT (Keep Term), and revaluation.
*   **Notifications**: Receive real-time updates from the college.
*   **Hall Tickets**: Download exam hall tickets directly.

### 👩‍🏫 Staff Module
*   **Class Management**: Take attendance and manage student records.
*   **Grading**: Enter internal and external marks.
*   **Leave Management**: Apply for leave and view status.
*   **Feedback**: Send and receive feedback from students.

### 👨‍💼 Admin & HOD Module
*   **Dashboard**: Comprehensive overview of college statistics.
*   **User Management**: Manage students, staff, and HODs.
*   **Course & Subject**: Configure courses, subjects, and sessions.
*   **Exam Control**: Schedule exams, generate hall tickets, and publish results.
*   **Reports**: Generate detailed reports on attendance and performance.

---

## 🛠️ Technology Stack

*   **Backend**: Python, Django
*   **Frontend**: HTML5, CSS3, JavaScript, Bootstrap, AdminLTE
*   **Database**: SQLite (Development), PostgreSQL (Production)
*   **PDF Generation**: xhtml2pdf
*   **Deployment**: Render / Heroku

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

---

## ☁️ Deployment

This project is configured for easy deployment on **Render**.

1.  Push your code to GitHub.
2.  Create a new Web Service on Render.
3.  Connect your repository.
4.  Render will automatically detect the `render.yaml` configuration.

For a detailed guide, check out [DEPLOYMENT.md](deployment_guide.md).

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📞 Support

If you have any questions or run into issues, please open an issue on the GitHub repository.

---

*Made with ❤️ by Vigneshraj Nadar*
