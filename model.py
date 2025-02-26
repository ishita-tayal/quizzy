from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the database
db = SQLAlchemy()

# Define the Admin model (Fixed Credentials)
class Admin(db.Model):
    admin_id = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)

# Define the User model
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)

# Define the Subject model
class Subject(db.Model):
    subject_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete-orphan", lazy=True)

# Define the Chapter model
class Chapter(db.Model):
    chapter_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    quizzes = db.relationship('Quiz', backref='chapter', cascade="all, delete-orphan", lazy=True)

# Define the Quiz model
class Quiz(db.Model):
    quiz_id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.chapter_id', ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_duration = db.Column(db.String(5), nullable=False)  # Format: HH:MM

    scores = db.relationship("Score", back_populates="quiz", cascade="all, delete-orphan")
    questions = db.relationship("Question", backref="quiz", cascade="all, delete-orphan")


# Define the Question model
class Question(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.quiz_id', ondelete="CASCADE"), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  # 1, 2, 3, or 4

# Define the Score model
class Score(db.Model):
    score_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)

    quiz = db.relationship("Quiz", back_populates="scores")
    user = db.relationship("User", backref="scores")


# Function to initialize the database with the hard-coded admin credential
def initialize_database(app):
    with app.app_context():
        db.create_all()
        
        admin = Admin.query.get("admin@quizzy.com")
        if admin:
            admin.password = "admin" 
        else:
            admin = Admin(admin_id="admin@quizzy.com", password="admin")
            db.session.add(admin)
        db.session.commit()
