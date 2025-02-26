#importing necessary modules
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from model import db, User, Admin, Score, Question, Quiz, Chapter, Subject, initialize_database
from datetime import datetime
from sqlalchemy.orm import joinedload

#initialising the app
app = Flask(__name__, instance_relative_config=True)
app.secret_key = "quizzy"

app.config["SQLALCHEMY_DATABASE_URI"] = r"sqlite:///C:\Users\Ishita Tayal\Desktop\MAD1-PROJECT\projectdb.db"

db.init_app(app)

#initialising the database
with app.app_context():
    initialize_database(app)

#route to the main page
@app.route("/")
def index():
    return render_template("index.html")

#------------------------------------USER ROUTES BEGIN HERE-------------------------------------

#functionality for user login
@app.route("/user/user_login", methods = ["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session["user_id"] = user.user_id 
            session["user_name"] = user.full_name 
            flash("Login successful! Welcome back.", "success")
            return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid email or password. Please try again.", "danger")
    return render_template("user/user_login.html")

#functionality for user signup
@app.route("/user/user_signup", methods = ["GET", "POST"])
def user_signup():
    if request.method == "POST":
        name = request.form["fullname"]
        mail = request.form["email"]
        pwd = request.form["password"]
        edu = request.form["qualification"]
        birth_date = request.form["dob"]

        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()

        if User.query.filter_by(email=mail).first():
            flash("This email is already in use. Try logging in.", "danger")
            return redirect(url_for("user_signup"))

        new_user = User(
            full_name=name,
            email=mail,
            password=pwd,
            qualification=edu,
            dob=birth_date
        )

        db.session.add(new_user)
        db.session.commit()
    
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for("user_login"))
    
    return render_template("user/user_signup.html")

#functionality to show user dashboard and display details on it
@app.route("/user/user_dashboard")
def user_dashboard():
    quizzes = db.session.query(
        Quiz.quiz_id, Quiz.title, Quiz.date_of_quiz, 
        Quiz.time_duration, Chapter.name.label("chapter_name"), 
        Subject.name.label("subject_name")
    ).join(Chapter, Quiz.chapter_id == Chapter.chapter_id) \
     .join(Subject, Chapter.subject_id == Subject.subject_id) \
     .all()

    return render_template("user/user_dashboard.html", quizzes=quizzes)

#functionality to show user profile and display the details of the users
@app.route("/user/user_profile")
def user_profile():
    user = User.query.get(session['user_id']) 
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('user_dashboard'))
    
    return render_template('user/user_profile.html', user=user)

#functionality to display the quiz details using the quiz ID
@app.route("/user/quiz_details/<int:quiz_id>")
def user_quiz_details(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template("user/user_quizdetails.html", quiz=quiz)

#functionality to start the quiz and attempt the questions
@app.route("/user/start_quiz/<int:quiz_id>")
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    try:
        time_duration = int(quiz.time_duration.split(":")[0] * 60 + quiz.time_duration.split(":")[1])
    except ValueError:
        time_duration = 10

    return render_template("user/user_quiz.html", quiz=quiz, questions=questions, quiz_duration=time_duration)

#functionality to submit the quiz and records its scores
@app.route("/user/submit_quiz/<int:quiz_id>", methods=["POST"])
def submit_quiz(quiz_id):
    if "user_id" not in session:
        flash("You must be logged in to submit a quiz.", "danger")
        return redirect(url_for("user_login"))

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    user_score = 0
    total_questions = len(questions)

    for question in questions:
        user_answer = request.form.get(f"question_{question.question_id}")
        if user_answer and user_answer == getattr(question, f"option{question.correct_option}"):
            user_score += 1

    # store score in the database and later display it
    new_score = Score(
        quiz_id=quiz_id,
        user_id=session["user_id"],
        time_stamp_of_attempt=datetime.utcnow(),
        total_scored=user_score
    )
    
    db.session.add(new_score)
    db.session.commit()

    flash(f"Quiz submitted! You scored {user_score}/{total_questions}.", "success")
    return redirect(url_for("user_dashboard"))

#route to display the user's score 
@app.route("/user/scores")
def user_scores():
    if "user_id" not in session:
        flash("You must be logged in to view your scores.", "danger")
        return redirect(url_for("user_login"))

    user_scores = db.session.query(
        Score.quiz_id, Score.total_scored, Score.time_stamp_of_attempt, 
        Quiz.title.label("quiz_title"), Quiz.time_duration,
        db.func.count(Question.question_id).label("total_questions")
    ).join(Quiz, Score.quiz_id == Quiz.quiz_id) \
     .join(Question, Quiz.quiz_id == Question.quiz_id) \
     .filter(Score.user_id == session["user_id"]) \
     .group_by(Score.quiz_id, Score.total_scored, Score.time_stamp_of_attempt, Quiz.title, Quiz.time_duration) \
     .order_by(Score.time_stamp_of_attempt.desc()) \
     .all()

    return render_template("user/user_scores.html", user_scores=user_scores)

#route to print the user summary
@app.route("/user/summary")
def user_summary():
    if "user_id" not in session:
        flash("You must be logged in to view your summary.", "danger")
        return redirect(url_for("user_login"))

    # query to fetch the last 5 quiz attempts
    user_scores = db.session.query(
        Quiz.title, Score.total_scored, db.func.count(Question.question_id).label("total_questions")
    ).join(Score, Quiz.quiz_id == Score.quiz_id) \
     .join(Question, Quiz.quiz_id == Question.quiz_id) \
     .filter(Score.user_id == session["user_id"]) \
     .group_by(Score.time_stamp_of_attempt, Quiz.title, Score.total_scored) \
     .order_by(Score.time_stamp_of_attempt.desc()) \
     .limit(5) \
     .all()

    # count quizzes attempted per subject
    subject_counts = db.session.query(
        Subject.name.label("subject_name"),
        db.func.count(Quiz.quiz_id).label("quiz_count")
    ).join(Chapter, Quiz.chapter_id == Chapter.chapter_id) \
     .join(Subject, Chapter.subject_id == Subject.subject_id) \
     .join(Score, Quiz.quiz_id == Score.quiz_id) \
     .filter(Score.user_id == session["user_id"]) \
     .group_by(Subject.subject_id) \
     .all()

    # convert subject attempts into percentages
    total_quizzes = sum(subject.quiz_count for subject in subject_counts)
    subject_labels = [subject.subject_name for subject in subject_counts]
    subject_ratios = [(subject.quiz_count / total_quizzes) * 100 for subject in subject_counts]

    return render_template("user/user_summary.html", 
                           quiz_labels=[score.title for score in user_scores], 
                           quiz_scores=[(score.total_scored / score.total_questions) * 100 for score in user_scores],
                           subject_labels=subject_labels, subject_ratios=subject_ratios)

#functionality for a user to search quizzes based on their titles
@app.route("/user/search", methods=["GET"])
def user_search():
    query = request.args.get("query", "").strip()

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for("user_dashboard"))
    
    quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()

    return render_template("user/user_search_results.html", query=query, quizzes=quizzes)

#-----------------------------------ADMIN ROUTES BEGIN HERE------------------------------------------
#functionality to login to the admin portal
@app.route("/admin/admin_login", methods = ["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin_id = request.form["admin_id"]
        password = request.form["password"]

        admin = Admin.query.filter_by(admin_id=admin_id, password=password).first()

        if admin:
            session["admin_id"] = admin.admin_id  # store admin session
            flash("Login successful!", "success")
            return redirect(url_for("admin_dashboard"))  # redirect to admin panel
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("admin/admin_login.html")

#display subjects on the admin dashboard
@app.route("/admin/admin_dashboard")
def admin_dashboard():
    subjects = Subject.query.all()  # fetch all subjects from the database
    return render_template("admin/admin_dashboard.html", subjects=subjects)

#functionality to add a subject on the admin dashboard to further make chapters and quizzes
@app.route("/admin/add_subject", methods=["POST"])
def add_subject():
    if "admin_id" not in session:
        flash("You must be logged in as an admin.", "danger")
        return redirect(url_for("admin_login"))

    name = request.form.get("name")
    description = request.form.get("description", "")

    if Subject.query.filter_by(name=name).first():
        flash("Subject already exists!", "warning")
        return redirect(url_for("admin_dashboard"))

    new_subject = Subject(name=name, description=description)
    db.session.add(new_subject)
    db.session.commit()

    flash("Subject added successfully!", "success")
    return redirect(url_for("admin_dashboard"))

#functionality to edit subject information
@app.route("/admin/edit_subject/<int:subject_id>", methods=["POST"])
def edit_subject(subject_id):
    if "admin_id" not in session:
        flash("You must be logged in as an admin.", "danger")
        return redirect(url_for("admin_login"))

    subject = Subject.query.get_or_404(subject_id)
    subject.name = request.form.get("name")
    subject.description = request.form.get("description")

    db.session.commit()
    flash("Subject updated successfully!", "success")
    return redirect(url_for("admin_dashboard"))

#functionality to delete the subject
@app.route("/admin/delete_subject/<int:subject_id>", methods=["POST"])
def delete_subject(subject_id):
    if "admin_id" not in session:
        flash("You must be logged in as an admin.", "danger")
        return redirect(url_for("admin_login"))

    subject = Subject.query.get_or_404(subject_id)

    # explicitly delete related chapters before deleting the subject
    for chapter in subject.chapters:
        db.session.delete(chapter)

    db.session.delete(subject)
    db.session.commit()

    flash("Subject and its chapters deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))

#route to display subject details using the subject ID
@app.route("/admin/subject/<int:subject_id>")
def subject_details(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template("admin/subject_details.html", subject=subject)

#functionality to add a chapter to the subject
@app.route("/admin/add_chapter/<int:subject_id>", methods=["POST"])
def add_chapter(subject_id):
    name = request.form.get("name")
    description = request.form.get("description")

    if not name:
        flash("Chapter name is required.", "danger")
        return redirect(url_for("subject_details", subject_id=subject_id))

    new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
    db.session.add(new_chapter)
    db.session.commit()
    flash("Chapter added successfully!", "success")

    return redirect(url_for("subject_details", subject_id=subject_id))

#functionality to edit a chapter in the subject
@app.route("/admin/edit_chapter/<int:chapter_id>", methods=["POST"])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    chapter.name = request.form.get("name")
    chapter.description = request.form.get("description")

    db.session.commit()
    flash("Chapter updated successfully!", "success")

    return redirect(url_for("subject_details", subject_id=chapter.subject_id))

#functionality to delete a chapter in the subject which also deletes its quizzes
@app.route("/admin/delete_chapter/<int:chapter_id>", methods=["POST"])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id

    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", "success")

    return redirect(url_for("subject_details", subject_id=subject_id))

#functionality to add a quiz in a chapter
@app.route("/admin/add_quiz/<int:chapter_id>", methods=["POST"])
def add_quiz(chapter_id):
    title = request.form.get("title")
    time_duration = request.form.get("time_duration")

    if not title or not time_duration:
        flash("Quiz title and duration are required.", "danger")
        return redirect(url_for("subject_details", subject_id=Chapter.query.get(chapter_id).subject_id))

    new_quiz = Quiz(title=title, chapter_id=chapter_id, time_duration=time_duration)
    db.session.add(new_quiz)
    db.session.commit()

    flash("Quiz created successfully!", "success")
    return redirect(url_for("quiz_details", quiz_id=new_quiz.quiz_id))

#functionality to add a question in a quiz 
@app.route("/admin/add_question/<int:quiz_id>", methods=["POST"])
def add_question(quiz_id):
    question_statement = request.form.get("question_statement")
    option1 = request.form.get("option1")
    option2 = request.form.get("option2")
    option3 = request.form.get("option3")
    option4 = request.form.get("option4")
    correct_option = request.form.get("correct_option")  # 1, 2, 3, or 4

    if not all([question_statement, option1, option2, option3, option4, correct_option]):
        flash("All fields are required.", "danger")
        return redirect(url_for("quiz_details", quiz_id=quiz_id))

    new_question = Question(
        quiz_id=quiz_id,
        question_statement=question_statement,
        option1=option1,
        option2=option2,
        option3=option3,
        option4=option4,
        correct_option=int(correct_option),
    )

    db.session.add(new_question)
    db.session.commit()

    flash("Question added successfully!", "success")
    return redirect(url_for("quiz_details", quiz_id=quiz_id))

#route to view the quiz through it's ID
@app.route("/admin/quiz/<int:quiz_id>")
def quiz_details(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template("admin/quiz_details.html", quiz=quiz)

#functionality to make searches in the admin portal using users, subjects and quizzes as criteria
@app.route("/admin/search", methods=["GET"])
def admin_search():
    query = request.args.get("query", "").strip()

    if not query:
        flash("Please enter a search term.", "warning")
        return redirect(url_for("admin_dashboard"))

    users = User.query.filter(
        (User.full_name.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))
    ).all()

    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()

    quizzes = Quiz.query.join(Chapter).filter(
        (Quiz.title.ilike(f"%{query}%")) | (Chapter.name.ilike(f"%{query}%"))
    ).all()

    return render_template(
        "admin/search_results.html",
        query=query,
        users=users,
        subjects=subjects,
        quizzes=quizzes
    )

#to show the user after search
@app.route('/user/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/admin_userprofile.html', user=user)

#to show the subject after search
@app.route('/subject/<int:subject_id>')
def view_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('admin/subject_details.html', subject=subject)

#to show the quiz after search
@app.route('/quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('admin/quiz_details.html', quiz=quiz)

#route for showing the summary on the admin portal
@app.route("/admin/statistics")
def admin_statistics():
    # Count total users, subjects, and quizzes
    user_count = User.query.count()
    subject_count = Subject.query.count()
    quiz_count = Quiz.query.count()

    # Fetch subjects and count quizzes through chapters
    subjects = Subject.query.options(joinedload(Subject.chapters)).all()

    subject_names = []
    quiz_counts = []

    for subject in subjects:
        total_quizzes = sum(len(chapter.quizzes) for chapter in subject.chapters)
        subject_names.append(subject.name)
        quiz_counts.append(total_quizzes)

    return render_template(
        "admin/statistics.html",
        user_count=user_count,
        subject_count=subject_count,
        quiz_count=quiz_count,
        subject_names=subject_names,
        quiz_counts=quiz_counts
    )

#edit quiz functionality
@app.route("/admin/edit_quiz/<int:quiz_id>", methods=["GET", "POST"])
def edit_quiz(quiz_id):
    if "admin_id" not in session:
        flash("You must be logged in as an admin.", "danger")
        return redirect(url_for("admin_login"))

    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == "POST":
        quiz.title = request.form.get("title")
        quiz.date_of_quiz = datetime.strptime(request.form.get("date_of_quiz"), "%Y-%m-%d")
        quiz.time_duration = request.form.get("time_duration")
        db.session.commit()
        flash("Quiz updated successfully!", "success")
        return redirect(url_for("quiz_details", quiz_id=quiz.quiz_id))
    
    return render_template("admin/edit_quiz.html", quiz=quiz)

#functionality to delete a quiz and its questions
@app.route("/admin/delete_quiz/<int:quiz_id>", methods=["POST"])
def delete_quiz(quiz_id):
    if "admin_id" not in session:
        flash("You must be logged in as an admin.", "danger")
        return redirect(url_for("admin_login"))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))

# edit a question route
@app.route("/admin/edit_question/<int:question_id>", methods=["POST"])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    question.question_statement = request.form.get("question_statement")
    question.option1 = request.form.get("option1")
    question.option2 = request.form.get("option2")
    question.option3 = request.form.get("option3")
    question.option4 = request.form.get("option4")
    question.correct_option = int(request.form.get("correct_option"))
    db.session.commit()
    flash("Question updated successfully!", "success")
    return redirect(url_for("quiz_details", quiz_id=question.quiz_id))

#route to delete a question
@app.route("/admin/delete_question/<int:question_id>", methods=["POST"])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully!", "success")
    return redirect(url_for("quiz_details", quiz_id=quiz_id))

#route to show a list of all quizzes to the admin under the quizzes tab
@app.route("/admin/all_quizzes")
def all_quizzes():
    quizzes = db.session.query(
        Quiz.quiz_id, Quiz.title, Quiz.date_of_quiz, Quiz.time_duration, Chapter.name.label("chapter_name"), Subject.name.label("subject_name")
    ).join(Chapter, Quiz.chapter_id == Chapter.chapter_id) \
     .join(Subject, Chapter.subject_id == Subject.subject_id) \
     .order_by(Quiz.date_of_quiz.desc()).all()
    
    return render_template("admin/all_quizzes.html", quizzes=quizzes)

#finally run the program
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7000)
