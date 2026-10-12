import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from database.database import db
from models.user import User
from models.assignment import Assignment
from models.subject import Subject
from models.note import Note
from models.schedule import Schedule

# =========================================================
# ACADEXA
# Intelligent Academic Management Platform
# =========================================================
load_dotenv()
app = Flask(__name__)


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///acadexa.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

db.init_app(app)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# REGISTRATION PAGE
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    # -----------------------------------------------------
    # Display registration page
    # -----------------------------------------------------

    if request.method == "GET":

        return render_template("register.html")


    # -----------------------------------------------------
    # Receive registration form
    # -----------------------------------------------------

    name = request.form.get("name", "").strip()

    email = request.form.get("email", "").strip().lower()

    password = request.form.get("password", "").strip()

    course = request.form.get("course", "").strip()

    semester = request.form.get("semester", "").strip()


    # -----------------------------------------------------
    # Basic validation
    # -----------------------------------------------------

    if not name or not email or not password:

        flash("Please fill in all required fields.", "error")

        return redirect(url_for("register"))


    # -----------------------------------------------------
    # Check whether email already exists
    # -----------------------------------------------------

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:

        flash(
            "An account with this email already exists.",
            "error"
        )

        return redirect(url_for("register"))


    # -----------------------------------------------------
    # Convert semester to integer
    # -----------------------------------------------------

    semester_number = None

    if semester:

        try:

            semester_number = int(semester)

        except ValueError:

            flash(
                "Please select a valid semester.",
                "error"
            )

            return redirect(url_for("register"))


    # -----------------------------------------------------
    # Secure password hashing
    # -----------------------------------------------------

    hashed_password = generate_password_hash(password)


    # -----------------------------------------------------
    # Create new User object
    # -----------------------------------------------------

    new_user = User(

        name=name,

        email=email,

        password=hashed_password,

        course=course,

        semester=semester_number,

        role="student"

    )


    # -----------------------------------------------------
    # Save user to database
    # -----------------------------------------------------

    try:

        db.session.add(new_user)

        db.session.commit()

        flash(
            "Account created successfully! You can now sign in.",
            "success"
        )

        return redirect(url_for("login"))

    except Exception as error:

        db.session.rollback()

        print("Registration error:", error)

        flash(
            "Something went wrong. Please try again.",
            "error"
        )

        return redirect(url_for("register"))


# =========================================================
# LOGIN PAGE
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    # -----------------------------------------------------
    # Display login page
    # -----------------------------------------------------

    if request.method == "GET":

        return render_template("login.html")


    # -----------------------------------------------------
    # Get login information
    # -----------------------------------------------------

    email = request.form.get("email", "").strip().lower()

    password = request.form.get("password", "").strip()


    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if not email or not password:

        flash(
            "Please enter your email and password.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Find user by email
    # -----------------------------------------------------

    user = User.query.filter_by(email=email).first()


    # -----------------------------------------------------
    # Check whether user exists
    # -----------------------------------------------------

    if user is None:

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Verify password
    # -----------------------------------------------------

    if not check_password_hash(user.password, password):

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Create login session
    # -----------------------------------------------------

    session["user_id"] = user.id

    session["user_name"] = user.name

    session["user_email"] = user.email


    # -----------------------------------------------------
    # Successful login
    # -----------------------------------------------------

    flash(
        "Login successful!",
        "success"
    )

    return redirect(url_for("dashboard"))


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    # -----------------------------------------------------
    # Check whether user is logged in
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please sign in to access your dashboard.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Get logged-in user's ID
    # -----------------------------------------------------

    user_id = session["user_id"]


    # -----------------------------------------------------
    # Find user from database
    # -----------------------------------------------------

    user = db.session.get(
        User,
        user_id
    )


    # -----------------------------------------------------
    # Safety check
    # -----------------------------------------------------

    if user is None:

        session.clear()

        flash(
            "Your account could not be found.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Get dashboard statistics
    # -----------------------------------------------------

    total_assignments = Assignment.query.filter_by(
        user_id=user.id
    ).count()


    completed_assignments = Assignment.query.filter_by(
        user_id=user.id,
        status="Completed"
    ).count()


    pending_assignments = Assignment.query.filter_by(
        user_id=user.id,
        status="Pending"
    ).count()


    total_subjects = Subject.query.filter_by(
        user_id=user.id
    ).count()


    total_notes = Note.query.filter_by(
        user_id=user.id
    ).count()


    # -----------------------------------------------------
    # Calculate assignment completion percentage
    # -----------------------------------------------------

    if total_assignments > 0:

        completion_percentage = round(
            (completed_assignments / total_assignments) * 100
        )

    else:

        completion_percentage = 0


    # -----------------------------------------------------
    # Get upcoming assignments
    # -----------------------------------------------------

    upcoming_assignments = Assignment.query.filter(
        Assignment.user_id == user.id,
        Assignment.status != "Completed"
    ).order_by(
        Assignment.due_date.asc()
    ).limit(3).all()
      # Today's schedule events

    from datetime import date

    today = date.today()

    today_schedule = Schedule.query.filter(
        Schedule.user_id == user.id,
        Schedule.event_date == today
    ).order_by(
        Schedule.start_time.asc()
    ).all()


    # Count overdue assignments

    overdue_assignments = Assignment.query.filter(
        Assignment.user_id == user.id,
        Assignment.status != "Completed",
        Assignment.due_date < today
    ).count()


    # Recent assignments

    recent_assignments = Assignment.query.filter_by(
        user_id=user.id
    ).order_by(
        Assignment.id.desc()
    ).limit(3).all()


    # Recent notes

    recent_notes = Note.query.filter_by(
        user_id=user.id
    ).order_by(
        Note.id.desc()
    ).limit(3).all()


    # Recent subjects

    recent_subjects = Subject.query.filter_by(
        user_id=user.id
    ).order_by(
        Subject.id.desc()
    ).limit(3).all()


    # -----------------------------------------------------
    # Display dashboard
    # -----------------------------------------------------

    return render_template(
        "dashboard.html",
        user=user,
        total_assignments=total_assignments,
        completed_assignments=completed_assignments,
        pending_assignments=pending_assignments,
        total_subjects=total_subjects,
        total_notes=total_notes,
        completion_percentage=completion_percentage,
        upcoming_assignments=upcoming_assignments,
        today_schedule=today_schedule,
        recent_assignments=recent_assignments,
        recent_notes=recent_notes,
        recent_subjects=recent_subjects,
        overdue_assignments=overdue_assignments,
        current_date=today
     )
    

# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings")
def settings():

    if "user_id" not in session:
        flash(
            "Please sign in to access your settings.",
            "error"
        )
        return redirect(url_for("login"))

    user_id = session["user_id"]

    user = db.session.get(
        User,
        user_id
    )

    if user is None:
        session.clear()
        flash(
            "Your account could not be found.",
            "error"
        )
        return redirect(url_for("login"))

    return render_template(
        "settings.html",
        user=user
    )


# =========================================================
# UPDATE PROFILE
# =========================================================

@app.route("/settings/update", methods=["POST"])
def update_profile():

    if "user_id" not in session:
        flash(
            "Please sign in to update your profile.",
            "error"
        )
        return redirect(url_for("login"))

    user_id = session["user_id"]

    user = db.session.get(
        User,
        user_id
    )

    if user is None:
        session.clear()
        flash(
            "Your account could not be found.",
            "error"
        )
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    course = request.form.get("course", "").strip()
    semester = request.form.get("semester", "").strip()

    if not name or not course or not semester:
        flash(
            "Please fill in all profile fields.",
            "error"
        )
        return redirect(url_for("settings"))

    user.name = name
    user.course = course
    user.semester = semester

    db.session.commit()

    session["user_name"] = user.name

    flash(
        "Profile updated successfully.",
        "success"
    )

    return redirect(url_for("settings"))
# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("login"))




# =========================================================
# ASSIGNMENTS PAGE
# =========================================================

@app.route("/assignments")
def assignments():

    if "user_id" not in session:
        flash("Please sign in to access your assignments.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    user = db.session.get(User, user_id)

    if user is None:
        session.clear()
        flash("Your account could not be found.", "error")
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()
    priority_filter = request.args.get("priority", "").strip()
    subject_filter = request.args.get("subject", "").strip()

    query = Assignment.query.filter_by(user_id=user_id)

    if search:
        query = query.filter(
            (Assignment.title.ilike(f"%{search}%"))
            |
            (Assignment.subject.ilike(f"%{search}%"))
        )

    if status_filter:
        query = query.filter(
            Assignment.status == status_filter
        )

    if priority_filter:
        query = query.filter(
            Assignment.priority == priority_filter
        )

    if subject_filter:
        query = query.filter(
            Assignment.subject == subject_filter
        )

    user_assignments = query.order_by(
        Assignment.due_date.asc()
    ).all()

       # Get all available subjects dynamically
    subject_options = set()

    # Subjects registered in the Subjects section
    registered_subjects = Subject.query.filter_by(
        user_id=user_id
    ).all()

    for subject in registered_subjects:
        if subject.name:
            subject_options.add(subject.name)

    # Subjects already used in assignments
    assignment_subjects = db.session.query(
        Assignment.subject
    ).filter(
        Assignment.user_id == user_id,
        Assignment.subject.isnot(None),
        Assignment.subject != ""
    ).distinct().all()

    for subject_name in assignment_subjects:
        subject_options.add(subject_name[0])

    # Sort subjects alphabetically
    subject_options = sorted(
        subject_options,
        key=str.lower
    )

    from datetime import date

    current_date = date.today()

    return render_template(
        "assignments.html",
        user=user,
        assignments=user_assignments,
        search=search,
        status_filter=status_filter,
        priority_filter=priority_filter,
        subject_filter=subject_filter,
        subject_options=subject_options,
        current_date=current_date
    )

@app.route("/assignments/add", methods=["GET", "POST"])
def add_assignment():

    # Check whether user is logged in
    if "user_id" not in session:

        flash(
            "Please sign in to add an assignment.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # Get current user
    user = db.session.get(
        User,
        session["user_id"]
    )

    if user is None:

        session.clear()

        flash(
            "Your account could not be found.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # -----------------------------------------------------
    # Display form
    # -----------------------------------------------------

    if request.method == "GET":

        # Get all available subjects dynamically
        subject_options = set()

        # Subjects registered in Subjects section
        registered_subjects = Subject.query.filter_by(
            user_id=session["user_id"]
        ).all()

        for subject in registered_subjects:

            if subject.name:

                subject_options.add(
                    subject.name
                )

        # Subjects already used in assignments
        assignment_subjects = db.session.query(
            Assignment.subject
        ).filter(
            Assignment.user_id == session["user_id"],
            Assignment.subject.isnot(None),
            Assignment.subject != ""
        ).distinct().all()

        for subject_name in assignment_subjects:

            subject_options.add(
                subject_name[0]
            )

        # Sort subjects alphabetically
        subject_options = sorted(
            subject_options,
            key=str.lower
        )

        return render_template(
            "add_assignment.html",
            user=user,
            subject_options=subject_options
        )

    # -----------------------------------------------------
    # Get form data
    # -----------------------------------------------------

    title = request.form.get(
        "title",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    due_date = request.form.get(
        "due_date",
        ""
    ).strip()

    priority = request.form.get(
        "priority",
        "Medium"
    )

    # -----------------------------------------------------
    # Validate required fields
    # -----------------------------------------------------

    if not title or not subject or not due_date:

        flash(
            "Please fill in all required fields.",
            "error"
        )

        return redirect(
            url_for("add_assignment")
        )

    # -----------------------------------------------------
    # Convert date
    # -----------------------------------------------------

    from datetime import datetime

    try:

        assignment_date = datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "Please enter a valid due date.",
            "error"
        )

        return redirect(
            url_for("add_assignment")
        )

    # -----------------------------------------------------
    # Create assignment
    # -----------------------------------------------------

    new_assignment = Assignment(
        title=title,
        subject=subject,
        description=description,
        due_date=assignment_date,
        priority=priority,
        status="Pending",
        user_id=user.id
    )

    # -----------------------------------------------------
    # Save assignment
    # -----------------------------------------------------

    try:

        db.session.add(new_assignment)

        db.session.commit()

        flash(
            "Assignment added successfully.",
            "success"
        )

        return redirect(
            url_for("assignments")
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Assignment error:",
            error
        )

        flash(
            "Something went wrong while saving the assignment.",
            "error"
        )

        return redirect(
            url_for("add_assignment")
        )
# =========================================================
# EDIT ASSIGNMENT
# =========================================================
@app.route("/assignments/edit/<int:assignment_id>", methods=["GET", "POST"])
def edit_assignment(assignment_id):

    # Check whether user is logged in
    if "user_id" not in session:

        flash(
            "Please sign in to edit an assignment.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # Find assignment belonging to current user
    assignment = Assignment.query.filter_by(
        id=assignment_id,
        user_id=session["user_id"]
    ).first()

    # Check whether assignment exists
    if assignment is None:

        flash(
            "Assignment not found.",
            "error"
        )

        return redirect(
            url_for("assignments")
        )

    # Get current user
    user = db.session.get(
        User,
        session["user_id"]
    )

    # -----------------------------------------------------
    # Display edit form
    # -----------------------------------------------------

    if request.method == "GET":

        # Get all available subjects dynamically
        subject_options = set()

        # Subjects registered in Subjects section
        registered_subjects = Subject.query.filter_by(
            user_id=session["user_id"]
        ).all()

        for subject in registered_subjects:

            if subject.name:

                subject_options.add(
                    subject.name
                )

        # Subjects already used in assignments
        assignment_subjects = db.session.query(
            Assignment.subject
        ).filter(
            Assignment.user_id == session["user_id"],
            Assignment.subject.isnot(None),
            Assignment.subject != ""
        ).distinct().all()

        for subject_name in assignment_subjects:

            subject_options.add(
                subject_name[0]
            )

        # Include current assignment subject
        # even if it is no longer registered
        if assignment.subject:

            subject_options.add(
                assignment.subject
            )

        # Sort subjects alphabetically
        subject_options = sorted(
            subject_options,
            key=str.lower
        )

        return render_template(
            "edit_assignment.html",
            assignment=assignment,
            user=user,
            subject_options=subject_options
        )

    # -----------------------------------------------------
    # Get updated form data
    # -----------------------------------------------------

    title = request.form.get(
        "title",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    due_date = request.form.get(
        "due_date",
        ""
    ).strip()

    priority = request.form.get(
        "priority",
        "Medium"
    )

    # -----------------------------------------------------
    # Validate required fields
    # -----------------------------------------------------

    if not title or not subject or not due_date:

        flash(
            "Please fill in all required fields.",
            "error"
        )

        return redirect(
            url_for(
                "edit_assignment",
                assignment_id=assignment.id
            )
        )

    # -----------------------------------------------------
    # Convert date
    # -----------------------------------------------------

    from datetime import datetime

    try:

        assignment_date = datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        flash(
            "Please enter a valid due date.",
            "error"
        )

        return redirect(
            url_for(
                "edit_assignment",
                assignment_id=assignment.id
            )
        )

    # -----------------------------------------------------
    # Update assignment
    # -----------------------------------------------------

    assignment.title = title
    assignment.subject = subject
    assignment.description = description
    assignment.due_date = assignment_date
    assignment.priority = priority

    # -----------------------------------------------------
    # Save changes
    # -----------------------------------------------------

    try:

        db.session.commit()

        flash(
            "Assignment updated successfully.",
            "success"
        )

        return redirect(
            url_for("assignments")
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Edit assignment error:",
            error
        )

        flash(
            "Something went wrong while updating the assignment.",
            "error"
        )

        return redirect(
            url_for(
                "edit_assignment",
                assignment_id=assignment.id
            )
        )

    # -----------------------------------------------------
    # Check login
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please sign in first.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Find user's assignment
    # -----------------------------------------------------

    assignment = Assignment.query.filter_by(
        id=assignment_id,
        user_id=session["user_id"]
    ).first()


    # -----------------------------------------------------
    # Check assignment
    # -----------------------------------------------------

    if assignment is None:

        flash(
            "Assignment not found.",
            "error"
        )

        return redirect(url_for("assignments"))


    # -----------------------------------------------------
    # Mark as completed
    # -----------------------------------------------------

    assignment.status = "Completed"


    # -----------------------------------------------------
    # Save change
    # -----------------------------------------------------

    try:

        db.session.commit()

        flash(
            "Assignment marked as completed.",
            "success"
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Complete assignment error:",
            error
        )

        flash(
            "Unable to update the assignment.",
            "error"
        )


    return redirect(
        url_for("assignments")
    )

# =========================================================
# COMPLETE ASSIGNMENT
# =========================================================

@app.route(
    "/assignments/complete/<int:assignment_id>",
    methods=["POST"]
)
def complete_assignment(assignment_id):

    # Check login
    if "user_id" not in session:

        flash(
            "Please sign in first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # Find user's assignment
    assignment = Assignment.query.filter_by(
        id=assignment_id,
        user_id=session["user_id"]
    ).first()

    # Check assignment
    if assignment is None:

        flash(
            "Assignment not found.",
            "error"
        )

        return redirect(
            url_for("assignments")
        )

    # Mark assignment as completed
    assignment.status = "Completed"

    # Save change
    try:

        db.session.commit()

        flash(
            "Assignment marked as completed.",
            "success"
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Complete assignment error:",
            error
        )

        flash(
            "Unable to update the assignment.",
            "error"
        )

    return redirect(
        url_for("assignments")
    )


# =========================================================
# DELETE ASSIGNMENT
# =========================================================

@app.route(
    "/assignments/delete/<int:assignment_id>",
    methods=["POST"]
)
def delete_assignment(assignment_id):

    # Check login
    if "user_id" not in session:

        flash(
            "Please sign in first.",
            "error"
        )

        return redirect(url_for("login"))


    # Find assignment belonging to current user
    assignment = Assignment.query.filter_by(
        id=assignment_id,
        user_id=session["user_id"]
    ).first()


    # Check whether assignment exists
    if assignment is None:

        flash(
            "Assignment not found.",
            "error"
        )

        return redirect(url_for("assignments"))


    # Delete assignment
    try:

        db.session.delete(assignment)

        db.session.commit()

        flash(
            "Assignment deleted successfully.",
            "success"
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Delete assignment error:",
            error
        )

        flash(
            "Unable to delete the assignment.",
            "error"
        )


    return redirect(
        url_for("assignments")
    )

# =========================================================
# SUBJECTS PAGE
# =========================================================

@app.route("/subjects")
def subjects():

    # -----------------------------------------------------
    # Check login
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please sign in to access your subjects.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Get current user
    # -----------------------------------------------------

    user_id = session["user_id"]

    user = db.session.get(User, user_id)


    if user is None:

        session.clear()

        flash(
            "Your account could not be found.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Get subjects belonging to this user
    # -----------------------------------------------------

    user_subjects = Subject.query.filter_by(
        user_id=user_id
    ).order_by(
        Subject.name.asc()
    ).all()

    # -----------------------------------------------------
    # Get assignment and note counts for each subject
    # -----------------------------------------------------

    for subject in user_subjects:

        subject.assignment_count = Assignment.query.filter_by(
            user_id=user_id,
            subject=subject.name
        ).count()

        subject.note_count = Note.query.filter_by(
            user_id=user_id,
            subject=subject.name
        ).count()
    # -----------------------------------------------------
    # Display subjects
    # -----------------------------------------------------

    return render_template(
        "subjects.html",
        user=user,
        subjects=user_subjects
    )


# =========================================================
# ADD SUBJECT
# =========================================================

@app.route("/subjects/add", methods=["GET", "POST"])
def add_subject():
    
# -----------------------------------------------------
# # Check login
# -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please sign in first.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Display form
    # -----------------------------------------------------

    if request.method == "GET":

        user = db.session.get(
            User,
            session["user_id"]
        )

        return render_template(
            "add_subject.html",
            user=user
        )


    # -----------------------------------------------------
    # Get form information
    # -----------------------------------------------------

    name = request.form.get(
        "name",
        ""
    ).strip()

    code = request.form.get(
        "code",
        ""
    ).strip()

    teacher = request.form.get(
        "teacher",
        ""
    ).strip()

    semester = request.form.get(
        "semester",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()


    # -----------------------------------------------------
    # Validate subject name
    # -----------------------------------------------------

    if not name:

        flash(
            "Please enter the subject name.",
            "error"
        )

        return redirect(
            url_for("add_subject")
        )
    # -----------------------------------------------------
    # Check for duplicate subject
    # -----------------------------------------------------

    existing_subject = Subject.query.filter_by(
        user_id=session["user_id"],
        name=name
    ).first()

    if existing_subject:

        flash(
            "This subject already exists.",
            "error"
        )

        return redirect(
            url_for("add_subject")
        )

    # -----------------------------------------------------
    # Convert semester
    # -----------------------------------------------------

    semester_number = None

    if semester:

        try:

            semester_number = int(semester)

        except ValueError:

            flash(
                "Please select a valid semester.",
                "error"
            )

            return redirect(
                url_for("add_subject")
            )


    # -----------------------------------------------------
    # Create subject
    # -----------------------------------------------------

    new_subject = Subject(

        name=name,

        code=code or None,

        teacher=teacher or None,

        semester=semester_number,

        description=description or None,

        user_id=session["user_id"]

    )


    # -----------------------------------------------------
    # Save subject
    # -----------------------------------------------------

    try:

        db.session.add(new_subject)

        db.session.commit()

        flash(
            "Subject added successfully.",
            "success"
        )

        return redirect(
            url_for("subjects")
        )


    except Exception as error:

        db.session.rollback()

        print(
            "Subject error:",
            error
        )

        flash(
            "Something went wrong while saving the subject.",
            "error"
        )

        return redirect(
            url_for("add_subject")
        )

# =========================================================
# EDIT SUBJECT
# =========================================================

@app.route(
    "/subjects/edit/<int:subject_id>",
    methods=["GET", "POST"]
)
def edit_subject(subject_id):

    # -----------------------------------------------------
    # Check login
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please sign in first.",
            "error"
        )

        return redirect(url_for("login"))


    # -----------------------------------------------------
    # Find subject
    # -----------------------------------------------------

    subject = db.session.get(
        Subject,
        subject_id
    )


    # -----------------------------------------------------
    # Check subject exists
    # -----------------------------------------------------

    if subject is None:

        flash(
            "Subject not found.",
            "error"
        )

        return redirect(url_for("subjects"))


    # -----------------------------------------------------
    # Check subject belongs to logged-in user
    # -----------------------------------------------------

    if subject.user_id != session["user_id"]:

        flash(
            "You are not allowed to edit this subject.",
            "error"
        )

        return redirect(url_for("subjects"))


    # -----------------------------------------------------
    # Display edit form
    # -----------------------------------------------------

    if request.method == "GET":

        user = db.session.get(
            User,
            session["user_id"]
        )

        return render_template(
            "edit_subject.html",
            user=user,
            subject=subject
        )


    # -----------------------------------------------------
    # Get updated information
    # -----------------------------------------------------

    name = request.form.get(
        "name",
        ""
    ).strip()

    code = request.form.get(
        "code",
        ""
    ).strip()

    teacher = request.form.get(
        "teacher",
        ""
    ).strip()

    semester = request.form.get(
        "semester",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()


    # -----------------------------------------------------
    # Validate subject name
    # -----------------------------------------------------

    if not name:

        flash(
            "Please enter the subject name.",
            "error"
        )

        return redirect(
            url_for(
                "edit_subject",
                subject_id=subject.id
            )
        )


    # -----------------------------------------------------
    # Convert semester
    # -----------------------------------------------------

    semester_number = None

    if semester:

        try:

            semester_number = int(semester)

        except ValueError:

            flash(
                "Please select a valid semester.",
                "error"
            )

            return redirect(
                url_for(
                    "edit_subject",
                    subject_id=subject.id
                )
            )


    # -----------------------------------------------------
    # Update subject
    # -----------------------------------------------------

    subject.name = name
    subject.code = code or None
    subject.teacher = teacher or None
    subject.semester = semester_number
    subject.description = description or None


    # -----------------------------------------------------
    # Save changes
    # -----------------------------------------------------

    try:

        db.session.commit()

        flash(
            "Subject updated successfully.",
            "success"
        )

        return redirect(
            url_for("subjects")
        )


    except Exception as error:

        db.session.rollback()

        print(
            "Subject update error:",
            error
        )

        flash(
            "Something went wrong while updating the subject.",
            "error"
        )

        return redirect(
            url_for(
                "edit_subject",
                subject_id=subject.id
            )
        )

# =========================================================
# DELETE SUBJECT
# =========================================================

@app.route(
    "/subjects/delete/<int:subject_id>",
    methods=["POST"]
)
def delete_subject(subject_id):

    # -----------------------------------------------------
    # Check login
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please sign in first.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # -----------------------------------------------------
    # Find subject
    # -----------------------------------------------------

    subject = db.session.get(
        Subject,
        subject_id
    )


    # -----------------------------------------------------
    # Check subject exists
    # -----------------------------------------------------

    if subject is None:

        flash(
            "Subject not found.",
            "error"
        )

        return redirect(
            url_for("subjects")
        )


    # -----------------------------------------------------
    # Make sure subject belongs to current user
    # -----------------------------------------------------

    if subject.user_id != session["user_id"]:

        flash(
            "You cannot delete this subject.",
            "error"
        )

        return redirect(
            url_for("subjects")
        )


    # -----------------------------------------------------
    # Delete subject
    # -----------------------------------------------------

    try:

        db.session.delete(subject)

        db.session.commit()

        flash(
            "Subject deleted successfully.",
            "success"
        )


    except Exception as error:

        db.session.rollback()

        print(
            "Delete subject error:",
            error
        )

        flash(
            "Unable to delete the subject.",
            "error"
        )


    return redirect(
        url_for("subjects")
    )

# =========================================================
# NOTES PAGE
# =========================================================

# =========================================================
# NOTES PAGE
# =========================================================

@app.route("/notes")
def notes():

    if "user_id" not in session:
        flash(
            "Please sign in to access your notes.",
            "error"
        )
        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    user = db.session.get(
        User,
        user_id
    )

    if user is None:
        session.clear()

        flash(
            "Your account could not be found.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # -----------------------------------------------------
    # Get filters from URL
    # -----------------------------------------------------

    subject_filter = request.args.get(
        "subject",
        ""
    ).strip()

    search = request.args.get(
        "search",
        ""
    ).strip()

    # -----------------------------------------------------
    # Get user's notes
    # -----------------------------------------------------

    notes_query = Note.query.filter_by(
        user_id=user_id
    )

    # -----------------------------------------------------
    # Apply subject filter
    # -----------------------------------------------------

    if subject_filter:

        notes_query = notes_query.filter(
            Note.subject == subject_filter
        )

    # -----------------------------------------------------
    # Apply search filter
    # -----------------------------------------------------

    if search:

        notes_query = notes_query.filter(
            (Note.title.ilike(f"%{search}%"))
            |
            (Note.content.ilike(f"%{search}%"))
        )

    # -----------------------------------------------------
    # Get filtered notes
    # -----------------------------------------------------

    user_notes = notes_query.order_by(
        Note.created_at.desc()
    ).all()

    # -----------------------------------------------------
    # Get all available subjects dynamically
    # -----------------------------------------------------

    subject_options = set()

    # Subjects registered in Subjects section

    registered_subjects = Subject.query.filter_by(
        user_id=user_id
    ).all()

    for subject in registered_subjects:

        if subject.name:

            subject_options.add(
                subject.name
            )

    # Subjects already used in notes

    note_subjects = db.session.query(
        Note.subject
    ).filter(
        Note.user_id == user_id,
        Note.subject.isnot(None),
        Note.subject != ""
    ).distinct().all()

    for subject_name in note_subjects:

        subject_options.add(
            subject_name[0]
        )

    # -----------------------------------------------------
    # Sort subjects alphabetically
    # -----------------------------------------------------

    subject_options = sorted(
        subject_options,
        key=str.lower
    )

    # -----------------------------------------------------
    # Display notes page
    # -----------------------------------------------------

    return render_template(
        "notes.html",
        user=user,
        notes=user_notes,
        subject_options=subject_options,
        subject_filter=subject_filter,
        search=search
    )


# =========================================================
# ADD NOTE
# =========================================================

@app.route("/notes/add", methods=["GET", "POST"])
def add_note():

    if "user_id" not in session:

        flash(
            "Please sign in to add a note.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    user = db.session.get(
        User,
        session["user_id"]
    )

    if user is None:

        session.clear()

        flash(
            "Your account could not be found.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # -----------------------------------------------------
    # Display add note form
    # -----------------------------------------------------

    if request.method == "GET":

        # Get all available subjects dynamically
        subject_options = set()

        # Subjects registered in Subjects section
        registered_subjects = Subject.query.filter_by(
            user_id=session["user_id"]
        ).all()

        for subject in registered_subjects:

            if subject.name:

                subject_options.add(
                    subject.name
                )

        # Subjects already used in notes
        note_subjects = db.session.query(
            Note.subject
        ).filter(
           Note.user_id == session["user_id"],
            Note.subject.isnot(None),
            Note.subject != ""
        ).distinct().all()

        for subject_name in note_subjects:

            subject_options.add(
                subject_name[0]
            )

        # Sort subjects alphabetically
        subject_options = sorted(
            subject_options,
            key=str.lower
        )

        return render_template(
            "add_note.html",
            user=user,
            subject_options=subject_options
        )

    # -----------------------------------------------------
    # Get form information
    # -----------------------------------------------------

    title = request.form.get(
        "title",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    content = request.form.get(
        "content",
        ""
    ).strip()

    # -----------------------------------------------------
    # Validate required fields
    # -----------------------------------------------------

    if not title or not content:

        flash(
            "Please enter a title and note content.",
            "error"
        )

        return redirect(
            url_for("add_note")
        )

    # -----------------------------------------------------
    # Create new note
    # -----------------------------------------------------

    new_note = Note(
        title=title,
        subject=subject or None,
        content=content,
        user_id=user.id
    )

    # -----------------------------------------------------
    # Save note
    # -----------------------------------------------------

    try:

        db.session.add(new_note)

        db.session.commit()

        flash(
            "Note added successfully.",
            "success"
        )

        return redirect(
            url_for("notes")
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Note error:",
            error
        )

        flash(
            "Something went wrong while saving the note.",
            "error"
        )

        return redirect(
            url_for("add_note")
        )



# =========================================================
# VIEW NOTE
# =========================================================

@app.route("/notes/view/<int:note_id>")
def view_note(note_id):

    if "user_id" not in session:
        flash(
            "Please sign in to view your note.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    note = Note.query.filter_by(
        id=note_id,
        user_id=session["user_id"]
    ).first()

    if note is None:
        flash(
            "Note not found.",
            "error"
        )

        return redirect(
            url_for("notes")
        )

    user = db.session.get(
        User,
        session["user_id"]
    )

    return render_template(
        "view_note.html",
        user=user,
        note=note
    )

# =========================================================
# EDIT NOTE
# =========================================================

@app.route("/notes/edit/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):

    if "user_id" not in session:
        flash(
            "Please sign in to edit your note.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    note = Note.query.filter_by(
        id=note_id,
        user_id=session["user_id"]
    ).first()

    if note is None:
        flash(
            "Note not found.",
            "error"
        )

        return redirect(
            url_for("notes")
        )

    user = db.session.get(
        User,
        session["user_id"]
    )

    # Display edit form
    if request.method == "GET":

        return render_template(
            "edit_note.html",
            user=user,
            note=note
        )

    # Get updated information
    title = request.form.get(
        "title",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    content = request.form.get(
        "content",
        ""
    ).strip()

    # Validate required fields
    if not title or not content:

        flash(
            "Please enter a title and note content.",
            "error"
        )

        return redirect(
            url_for(
                "edit_note",
                note_id=note.id
            )
        )

    # Update note
    note.title = title
    note.subject = subject or None
    note.content = content

    try:

        db.session.commit()

        flash(
            "Note updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "view_note",
                note_id=note.id
            )
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Edit note error:",
            error
        )

        flash(
            "Something went wrong while updating the note.",
            "error"
        )

        return redirect(
            url_for(
                "edit_note",
                note_id=note.id
            )
        )


# =========================================================
# DELETE NOTE
# =========================================================

@app.route("/notes/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):

    if "user_id" not in session:
        flash(
            "Please sign in first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    note = Note.query.filter_by(
        id=note_id,
        user_id=session["user_id"]
    ).first()

    if note is None:
        flash(
            "Note not found.",
            "error"
        )

        return redirect(
            url_for("notes")
        )

    try:

        db.session.delete(note)

        db.session.commit()

        flash(
            "Note deleted successfully.",
            "success"
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Delete note error:",
            error
        )

        flash(
            "Unable to delete the note.",
            "error"
        )

    return redirect(
        url_for("notes")
    )

# =========================================================
# SCHEDULE PAGE
# =========================================================
@app.route("/schedule")
def schedule():

    if "user_id" not in session:
        flash(
            "Please sign in to access your schedule.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    user_id = session["user_id"]

    user = db.session.get(
        User,
        user_id
    )

    if user is None:
        session.clear()

        flash(
            "Your account could not be found.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # Get all schedule events

    events = Schedule.query.filter_by(
        user_id=user_id
    ).order_by(
        Schedule.event_date.asc(),
        Schedule.start_time.asc()
    ).all()


    # Get today's date

    from datetime import date

    today = date.today()


    # Get today's events

    today_events = Schedule.query.filter(
        Schedule.user_id == user_id,
        Schedule.event_date == today
    ).order_by(
        Schedule.start_time.asc()
    ).all()


    # Get upcoming events

    upcoming_events = Schedule.query.filter(
        Schedule.user_id == user_id,
        Schedule.event_date > today
    ).order_by(
        Schedule.event_date.asc(),
        Schedule.start_time.asc()
    ).limit(5).all()


    return render_template(
        "schedule.html",
        user=user,
        events=events,
        today_events=today_events,
        upcoming_events=upcoming_events,
        current_date=today
    )



# =========================================================
# ADD SCHEDULE EVENT
# =========================================================

@app.route("/schedule/add", methods=["GET", "POST"])
def add_schedule_event():

    if "user_id" not in session:

        flash(
            "Please sign in to add an event.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    user = db.session.get(
        User,
        session["user_id"]
    )

    if user is None:

        session.clear()

        flash(
            "Your account could not be found.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # -----------------------------------------------------
    # Display form
    # -----------------------------------------------------

    if request.method == "GET":

        # Get all available subjects dynamically
        subject_options = set()

        # Subjects registered in Subjects section
        registered_subjects = Subject.query.filter_by(
            user_id=session["user_id"]
        ).all()

        for subject in registered_subjects:

            if subject.name:

                subject_options.add(
                    subject.name
                )

        # Subjects already used in schedule events
        schedule_subjects = db.session.query(
            Schedule.subject
        ).filter(
            Schedule.user_id == session["user_id"],
            Schedule.subject.isnot(None),
            Schedule.subject != ""
        ).distinct().all()

        for subject_name in schedule_subjects:

            subject_options.add(
                subject_name[0]
            )

        # Sort subjects alphabetically
        subject_options = sorted(
            subject_options,
            key=str.lower
        )

        return render_template(
            "add_schedule.html",
            user=user,
            subject_options=subject_options
        )

    # -----------------------------------------------------
    # Get form values
    # -----------------------------------------------------

    title = request.form.get(
        "title",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    event_date = request.form.get(
        "event_date",
        ""
    ).strip()

    start_time = request.form.get(
        "start_time",
        ""
    ).strip()

    end_time = request.form.get(
        "end_time",
        ""
    ).strip()

    event_type = request.form.get(
        "event_type",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    # -----------------------------------------------------
    # Validate required fields
    # -----------------------------------------------------

    if not title or not event_date:

        flash(
            "Please enter an event title and date.",
            "error"
        )

        return redirect(
            url_for("add_schedule_event")
        )

    # -----------------------------------------------------
    # Convert date and time strings
    # -----------------------------------------------------

    from datetime import datetime

    try:

        event_date_value = datetime.strptime(
            event_date,
            "%Y-%m-%d"
        ).date()

        start_time_value = None
        end_time_value = None

        if start_time:

            start_time_value = datetime.strptime(
                start_time,
                "%H:%M"
            ).time()

        if end_time:

            end_time_value = datetime.strptime(
                end_time,
                "%H:%M"
            ).time()

    except ValueError:

        flash(
            "Please enter a valid date or time.",
            "error"
        )

        return redirect(
            url_for("add_schedule_event")
        )

    # -----------------------------------------------------
    # Create new schedule event
    # -----------------------------------------------------

    new_event = Schedule(
        title=title,
        subject=subject or None,
        event_date=event_date_value,
        start_time=start_time_value,
        end_time=end_time_value,
        event_type=event_type or None,
        description=description or None,
        user_id=session["user_id"]
    )

    # -----------------------------------------------------
    # Save event
    # -----------------------------------------------------

    try:

        db.session.add(new_event)

        db.session.commit()

        flash(
            "Schedule event added successfully.",
            "success"
        )

        return redirect(
            url_for("schedule")
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Schedule event error:",
            error
        )

        flash(
            "Something went wrong while saving the event.",
            "error"
        )

        return redirect(
            url_for("add_schedule_event")
        )


# =========================================================
# EDIT SCHEDULE EVENT
# =========================================================

@app.route(
    "/schedule/edit/<int:event_id>",
    methods=["GET", "POST"]
)
def edit_schedule_event(event_id):

    if "user_id" not in session:

        flash(
            "Please sign in to edit your event.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    # -----------------------------------------------------
    # Find event belonging to current user
    # -----------------------------------------------------

    event = Schedule.query.filter_by(
        id=event_id,
        user_id=session["user_id"]
    ).first()

    if event is None:

        flash(
            "Schedule event not found.",
            "error"
        )

        return redirect(
            url_for("schedule")
        )

    user = db.session.get(
        User,
        session["user_id"]
    )

    # -----------------------------------------------------
    # Display edit form
    # -----------------------------------------------------

    if request.method == "GET":

        # Get all available subjects dynamically
        subject_options = set()

        # Subjects registered in Subjects section
        registered_subjects = Subject.query.filter_by(
            user_id=session["user_id"]
        ).all()

        for subject in registered_subjects:

            if subject.name:

                subject_options.add(
                    subject.name
                )

        # Subjects already used in schedule events
        schedule_subjects = db.session.query(
            Schedule.subject
        ).filter(
            Schedule.user_id == session["user_id"],
            Schedule.subject.isnot(None),
            Schedule.subject != ""
        ).distinct().all()

        for subject_name in schedule_subjects:

            subject_options.add(
                subject_name[0]
            )

        # Include current event subject
        # even if it is no longer registered
        if event.subject:

            subject_options.add(
                event.subject
            )

        # Sort subjects alphabetically
        subject_options = sorted(
            subject_options,
            key=str.lower
        )

        return render_template(
            "edit_schedule.html",
            user=user,
            event=event,
            subject_options=subject_options
        )

    # -----------------------------------------------------
    # Get updated form values
    # -----------------------------------------------------

    title = request.form.get(
        "title",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    event_date = request.form.get(
        "event_date",
        ""
    ).strip()

    start_time = request.form.get(
        "start_time",
        ""
    ).strip()

    end_time = request.form.get(
        "end_time",
        ""
    ).strip()

    event_type = request.form.get(
        "event_type",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    # -----------------------------------------------------
    # Validate required fields
    # -----------------------------------------------------

    if not title or not event_date:

        flash(
            "Please enter an event title and date.",
            "error"
        )

        return redirect(
            url_for(
                "edit_schedule_event",
                event_id=event.id
            )
        )

    # -----------------------------------------------------
    # Convert date and time
    # -----------------------------------------------------

    from datetime import datetime

    try:

        event.event_date = datetime.strptime(
            event_date,
            "%Y-%m-%d"
        ).date()

        event.start_time = (
            datetime.strptime(
                start_time,
                "%H:%M"
            ).time()
            if start_time
            else None
        )

        event.end_time = (
            datetime.strptime(
                end_time,
                "%H:%M"
            ).time()
            if end_time
            else None
        )

    except ValueError:

        flash(
            "Please enter a valid date or time.",
            "error"
        )

        return redirect(
            url_for(
                "edit_schedule_event",
                event_id=event.id
            )
        )

    # -----------------------------------------------------
    # Update event information
    # -----------------------------------------------------

    event.title = title
    event.subject = subject or None
    event.event_type = event_type or None
    event.description = description or None

    # -----------------------------------------------------
    # Save changes
    # -----------------------------------------------------

    try:

        db.session.commit()

        flash(
            "Schedule event updated successfully.",
            "success"
        )

        return redirect(
            url_for("schedule")
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Edit schedule error:",
            error
        )

        flash(
            "Unable to update the schedule event.",
            "error"
        )

        return redirect(
            url_for(
                "edit_schedule_event",
                event_id=event.id
            )
        )


# =========================================================
# DELETE SCHEDULE EVENT
# =========================================================

@app.route(
    "/schedule/delete/<int:event_id>",
    methods=["POST"]
)
def delete_schedule_event(event_id):

    if "user_id" not in session:
        flash(
            "Please sign in first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    event = Schedule.query.filter_by(
        id=event_id,
        user_id=session["user_id"]
    ).first()

    if event is None:
        flash(
            "Schedule event not found.",
            "error"
        )

        return redirect(
            url_for("schedule")
        )

    try:

        db.session.delete(event)

        db.session.commit()

        flash(
            "Schedule event deleted successfully.",
            "success"
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Delete schedule error:",
            error
        )

        flash(
            "Unable to delete the schedule event.",
            "error"
        )

    return redirect(
        url_for("schedule")
    )

# =========================================================
# PROGRESS & ANALYTICS
# =========================================================

@app.route("/progress")
def progress():

    # -----------------------------------------------------
    # Check whether user is logged in
    # -----------------------------------------------------

    if "user_id" not in session:

        flash(
            "Please sign in to view your progress.",
            "error"
        )

        return redirect(url_for("login"))

    # -----------------------------------------------------
    # Get current user
    # -----------------------------------------------------

    user_id = session["user_id"]

    user = db.session.get(
        User,
        user_id
    )

    # -----------------------------------------------------
    # Safety check
    # -----------------------------------------------------

    if user is None:

        session.clear()

        flash(
            "Your account could not be found.",
            "error"
        )

        return redirect(url_for("login"))

    # -----------------------------------------------------
    # Get user's academic data
    # -----------------------------------------------------

    total_assignments = Assignment.query.filter_by(
        user_id=user_id
    ).count()

    completed_assignments = Assignment.query.filter_by(
        user_id=user_id,
        status="Completed"
    ).count()

    pending_assignments = Assignment.query.filter_by(
        user_id=user_id,
        status="Pending"
    ).count()

    total_subjects = Subject.query.filter_by(
        user_id=user_id
    ).count()

    total_notes = Note.query.filter_by(
        user_id=user_id
    ).count()

    total_events = Schedule.query.filter_by(
        user_id=user_id
    ).count()

    # -----------------------------------------------------
    # Calculate assignment completion percentage
    # -----------------------------------------------------

    if total_assignments > 0:

        completion_percentage = round(
            (completed_assignments / total_assignments) * 100
        )

    else:

        completion_percentage = 0
   
    # -----------------------------------------------------
    # Find overdue assignments
    # -----------------------------------------------------

    from datetime import date

    overdue_assignments = Assignment.query.filter(
        Assignment.user_id == user_id,
        Assignment.status == "Pending",
        Assignment.due_date < date.today()
    ).count()


    # -----------------------------------------------------
    # Calculate assignment status percentages
    # -----------------------------------------------------

    if total_assignments > 0:

        completed_percentage = round(
            (completed_assignments / total_assignments) * 100
        )

        pending_percentage = round(
            (pending_assignments / total_assignments) * 100
        )

        overdue_percentage = round(
            (overdue_assignments / total_assignments) * 100
        )

    else:

        completed_percentage = 0
        pending_percentage = 0
        overdue_percentage = 0
    # -----------------------------------------------------
# Calculate assignment status percentages
# -----------------------------------------------------
# -----------------------------------------------------
    # Display progress page
    # -----------------------------------------------------

    return render_template(
        "progress.html",
        user=user,
        total_assignments=total_assignments,
        completed_assignments=completed_assignments,
        pending_assignments=pending_assignments,
        overdue_assignments=overdue_assignments,
        total_subjects=total_subjects,
        total_notes=total_notes,
        total_events=total_events,
        completion_percentage=completion_percentage,
        completed_percentage=completed_percentage,
        pending_percentage=pending_percentage,
        overdue_percentage=overdue_percentage
    )
# =========================================================
# CREATE DATABASE TABLES
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)
