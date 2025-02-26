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

# Define the Score model
class Score(db.Model):
    score_id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False)
    
    quiz = db.relationship("Quiz", back_populates="scores")
    user = db.relationship("User", backref="scores")

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
        subjects = [
            Subject(name="Mathematics", description="Covers algebra, calculus, and geometry."),
            Subject(name="Physics", description="Concepts of motion, energy, and thermodynamics."),
            Subject(name="Chemistry", description="Study of matter, reactions, and periodic table."),
            Subject(name="Biology", description="Understanding living organisms and ecosystems."),
            Subject(name="Computer Science", description="Programming, data structures, and algorithms."),
        ]
        db.session.add_all(subjects)
        db.session.commit()

        # Hardcoded Chapters, Quizzes, and Questions
        chapters_and_quizzes = [
            ("Algebra", subjects[0], [
                ("Linear Equations Quiz", [
                    ("Solve for x: 2x + 3 = 7", "2", "3", "4", "5", 1),
                    ("Find the slope of y = 3x + 2", "3", "2", "1", "0", 1),
                    ("Solve: x² - 4x + 4 = 0", "2", "4", "-2", "0", 1),
                    ("What is the discriminant of x² - 6x + 9?", "0", "3", "-3", "6", 1),
                    ("Find the sum of roots of x² - 5x + 6 = 0", "5", "6", "7", "8", 1)
                ]),
                ("Quadratic Equations Quiz", [
                    ("Find the roots of x² - 5x + 6 = 0", "2,3", "1,4", "-2,-3", "-1,-4", 1),
                    ("What is the sum of roots in a quadratic equation?", "-b/a", "b/a", "c/a", "-c/a", 1),
                    ("Solve x² - 9 = 0", "x=±3", "x=±9", "x=3", "x=-3", 1),
                    ("Discriminant of x² + 4x + 4 = 0", "0", "4", "16", "-4", 1),
                    ("Product of roots of x² - 7x + 10 = 0", "10", "-7", "-10", "7", 1)
                ])
            ]),
            ("Motion", subjects[1], [
                ("Newton's Laws Quiz", [
                    ("Which law states 'For every action, there is an equal and opposite reaction'?", "1st", "2nd", "3rd", "None", 3),
                    ("What is the SI unit of force?", "Joule", "Newton", "Watt", "Pascal", 2),
                    ("What is the formula for force?", "F = ma", "F = mv", "F = m/a", "F = m+v", 1),
                    ("Which force opposes motion?", "Gravity", "Friction", "Tension", "Normal", 2),
                    ("Which of these is not a type of force?", "Gravitational", "Magnetic", "Pressure", "Thermal", 4)
                ]),
                ("Energy and Work Quiz", [
                    ("What is the SI unit of work?", "Joule", "Newton", "Watt", "Pascal", 1),
                    ("Work is defined as?", "Force × Displacement", "Mass × Velocity", "Power × Time", "Pressure × Area", 1),
                    ("Which form of energy is stored in a stretched rubber band?", "Kinetic", "Potential", "Thermal", "Sound", 2),
                    ("What is power measured in?", "Joule", "Newton", "Watt", "Ampere", 3),
                    ("What is the work done when a force is perpendicular to displacement?", "Max", "Zero", "Negative", "Depends on mass", 2)
                ])
            ]),
            ("Organic Chemistry", subjects[2], [
                ("Hydrocarbons Quiz", [
                    ("Which of these is a saturated hydrocarbon?", "Alkane", "Alkene", "Alkyne", "Aromatic", 1),
                    ("What is the general formula of an alkane?", "CnH2n", "CnH2n+2", "CnH2n-2", "CnHn", 2),
                    ("What is the simplest alkene?", "Methane", "Ethene", "Propane", "Ethyne", 2),
                    ("Benzene is an example of?", "Alkane", "Alkene", "Aromatic", "Alkyne", 3),
                    ("What is the functional group of alcohols?", "-OH", "-COOH", "-CHO", "-CO", 1)
                ]),
                ("Chemical Reactions Quiz", [
                    ("Which reaction type involves oxygen?", "Combination", "Decomposition", "Oxidation", "Neutralization", 3),
                    ("Which gas is released in acid-metal reactions?", "Oxygen", "Hydrogen", "Nitrogen", "Carbon Dioxide", 2),
                    ("What is the pH of pure water?", "6", "7", "8", "9", 2),
                    ("What type of reaction is rusting?", "Oxidation", "Reduction", "Neutralization", "Combination", 1),
                    ("Which catalyst is used in the Haber process?", "Platinum", "Iron", "Nickel", "Copper", 2)
                ])
            ]),
            ("Genetics", subjects[3], [
                ("DNA & RNA Quiz", [
                    ("What is the shape of DNA?", "Helix", "Double Helix", "Sheet", "Coil", 2),
                    ("Which sugar is found in RNA?", "Ribose", "Deoxyribose", "Glucose", "Fructose", 1),
                    ("Which base is found in RNA but not DNA?", "Adenine", "Cytosine", "Uracil", "Thymine", 3),
                    ("What is the process of making RNA from DNA called?", "Translation", "Transcription", "Replication", "Mutation", 2),
                    ("Where does translation occur?", "Nucleus", "Mitochondria", "Ribosome", "Cytoplasm", 3)
                ]),
                ("Genetics Quiz", [
                    ("Who is known as the father of genetics?", "Darwin", "Mendel", "Watson", "Crick", 2),
                    ("What is a genotype?", "Physical trait", "Genetic makeup", "RNA sequence", "Protein", 2),
                    ("Which of these is a recessive trait?", "Brown eyes", "Blue eyes", "Curly hair", "Dark hair", 2),
                    ("What is a phenotype?", "Genetic makeup", "Physical trait", "DNA sequence", "Chromosome", 2),
                    ("What is the basic unit of heredity?", "Cell", "Gene", "Chromosome", "Protein", 2)
                ])
            ])
        ]

        for chapter_name, subject, quizzes in chapters_and_quizzes:
            chapter = Chapter(name=chapter_name, subject_id=subject.subject_id)
            db.session.add(chapter)
            db.session.commit()

            for quiz_title, questions in quizzes:
                quiz = Quiz(title=quiz_title, chapter_id=chapter.chapter_id, time_duration="00:15")
                db.session.add(quiz)
                db.session.commit()

                for question_text, opt1, opt2, opt3, opt4, correct in questions:
                    question = Question(quiz_id=quiz.quiz_id, question_statement=question_text,
                                        option1=opt1, option2=opt2, option3=opt3, option4=opt4,
                                        correct_option=correct)
                    db.session.add(question)
                    db.session.commit()

        db.session.commit()
