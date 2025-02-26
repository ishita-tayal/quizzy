# quizzy

## Description

This project is a full-fledged quiz management system designed for both admins and users. The system allows admins to create, manage, and schedule quizzes, while users can search, attempt, and track their quiz performance through interactive dashboards and performance charts.

## Technologies Used

- Flask  
- Flask-SQLAlchemy  
- SQLite  
- Jinja2  
- HTML, CSS, Bootstrap  
- JavaScript, Chart.js  

## Architecture

- **Routes**: Located in `app.py`, all user and admin routes handle quiz management, search functionality, quiz attempts, and result storage.
- **Models**: Defined in `model.py` using SQLAlchemy ORM, managing database relationships for users, quizzes, subjects, chapters, questions, and scores.
- **Templates (Frontend UI)**: All HTML files are inside the `templates/` folder, categorized as:
  - **Admin Templates**: `templates/admin/` for quiz creation and user tracking.
  - **User Templates**: `templates/user/` for quiz attempts, search results, and performance tracking.
- **Static Files**: Images are stored in the `static/` directory.
- **Database**: Uses SQLite.

## Features

### Authentication System
- Separate Admin and User login with a registration form.
- User authentication managed through a database model.

### Admin Dashboard
- **Manage Subjects & Chapters**: Admin can create, edit, and delete subjects and chapters.
- **Quiz Management**: Create quizzes with MCQ-based questions (one correct option), specify date and duration.
- **Search Functionality**: Admin can search for users, subjects, and quizzes.
- **Performance Overview**: Displays summary charts for quizzes and user activity.

### Quiz Management
- Admin can edit or delete quizzes and their questions.
- MCQ-based quizzes with a predefined date and duration (HH:MM format).

### User Dashboard
- Users can browse and attempt quizzes of their choice.
- **Quiz Timer**: Auto-submits the quiz upon completion.
- **Performance Tracking**: Records quiz scores and displays previous attempts.
- **Summary Charts**: Visual representation of quiz performance trends.
