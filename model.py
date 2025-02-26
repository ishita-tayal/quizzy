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
    email = db.Column(255, unique=True, nullable=False)
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
    time_duration = db.Column(db.String(5), nullable=False)
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
    correct_option = db.Column(db.Integer, nullable=False)

# Function to initialize the database with hardcoded data
def initialize_database(app):
    with app.app_context():
        db.create_all()

        # Ensure admin exists
        admin = Admin.query.get("admin@quizzy.com")
        if not admin:
            admin = Admin(admin_id="admin@quizzy.com", password="admin")
            db.session.add(admin)
        
        # Hardcoded Subjects
        math = Subject(name="Mathematics", description="Covers algebra, calculus, and geometry.")
        physics = Subject(name="Physics", description="Concepts of motion, energy, and thermodynamics.")
        chemistry = Subject(name="Chemistry", description="Study of matter, reactions, and periodic table.")
        
        db.session.add_all([math, physics, chemistry])
        db.session.commit()

        # Hardcoded Chapters and Quizzes
        chapters_and_quizzes = [
            (math, "Algebra", "Basics of algebra", [
                ("Linear Equations Quiz", "00:15", [
                    ("What is the value of x in 2x + 3 = 7?", "2", "3", "4", "5", 1),
                    ("Solve for y: 3y - 4 = 8", "3", "4", "5", "6", 2),
                    ("Find the slope of y = 2x + 5", "2", "5", "10", "1", 1),
                    ("What is 2(3x - 4) = 12?", "x = 2", "x = 3", "x = 4", "x = 5", 2)
                ]),
                ("Quadratic Equations Quiz", "00:15", [
                    ("Find the roots of x² - 5x + 6 = 0", "2 & 3", "1 & 4", "-2 & -3", "-1 & -4", 1),
                    ("What is the sum of roots in a quadratic equation?", "-b/a", "b/a", "c/a", "-c/a", 1),
                    ("Solve x² - 9 = 0", "x = ±3", "x = ±9", "x = 3", "x = -3", 1),
                    ("Discriminant of x² + 4x + 4 = 0", "0", "4", "16", "-4", 1)
                ])
            ]),
            (physics, "Motion", "Laws of motion", [
                ("Newton's Laws Quiz", "00:15", [
                    ("State Newton's first law", "Inertia", "Acceleration", "Force", "Momentum", 1),
                    ("What is the formula for force?", "F = ma", "F = mv", "F = m/a", "F = m+v", 1),
                    ("Unit of force in SI?", "Newton", "Joule", "Watt", "Dyne", 1),
                    ("Third law states?", "Action-reaction", "Motion", "Gravity", "Momentum", 1)
                ])
            ])
        ]
        
        for subject, chapter_name, chapter_desc, quizzes in chapters_and_quizzes:
            chapter = Chapter(name=chapter_name, subject_id=subject.subject_id, description=chapter_desc)
            db.session.add(chapter)
            db.session.commit()
            
            for quiz_title, duration, questions in quizzes:
                quiz = Quiz(title=quiz_title, chapter_id=chapter.chapter_id, time_duration=duration)
                db.session.add(quiz)
                db.session.commit()
                
                for question_text, opt1, opt2, opt3, opt4, correct in questions:
                    question = Question(
                        quiz_id=quiz.quiz_id,
                        question_statement=question_text,
                        option1=opt1, option2=opt2, option3=opt3, option4=opt4,
                        correct_option=correct
                    )
                    db.session.add(question)
                    db.session.commit()
        
        db.session.commit()
