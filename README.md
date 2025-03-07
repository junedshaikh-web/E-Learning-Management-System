📖 Overview

The E-Learning Management System (LMS) is a web-based platform built using Flask to manage online courses, student enrollments, and instructor-led classes efficiently. The system provides role-based access for students, instructors, and administrators to facilitate seamless learning and course management.

🚀 Features

🔐 Authentication & Authorization

- JWT-based authentication for secure login & session management

- Role-based access for students, instructors, and administrators

🎓 Course Management

- Instructors can create, update, and delete courses

- Students can enroll in courses and access content

📊 Student Enrollment & Progress Tracking

- Students can enroll in multiple courses

- Tracks enrollment history & learning progress

📋 Instructor Dashboard

- Manage assigned courses

- Track student enrollments

🛠 Admin Controls

- Manage users, courses, and enrollments

- Assign roles and monitor platform usage

⚡ API-Driven Backend

- RESTful APIs built with Flask

- Marshmallow for data serialization

- SQLAlchemy ORM for database operations

🏗 Tech Stack

- Backend:

- Flask

- Flask-SQLAlchemy

- Flask-JWT-Extended

- Flask-Marshmallow

- Flask-Migrate

◉ Database:

- PostgreSQL / MySQL / SQLite

- Authentication:

- JSON Web Tokens (JWT)

◉ API:

- RESTful API with Flask

🔧 Installation & Setup

1️⃣ Clone the Repository
```
git clone https://github.com/your-username/elearning-lms.git
cd elearning-lms
```

2️⃣ Create a Virtual Environment & Activate
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

3️⃣ Install Dependencies
```
pip install -r requirements.txt
```

4️⃣ Set Up Environment Variables
Create a .env file and configure your database & secret keys.
```
FLASK_APP=manage.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///lms.db
```

5️⃣ Initialize the Database
```
flask db init
flask db migrate -m "Initial Migration"
flask db upgrade
```

6️⃣ Run the Application
```
flask run
``