from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "super_secret_key"

# ---------------- DATABASE CONNECTION ----------------
def get_connection():
    conn = sqlite3.connect("student.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- CREATE TABLES ----------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT UNIQUE,
        name TEXT,
        marks INTEGER,
        grade TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- ADMIN LOGIN ----------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admins WHERE username=? AND password=?",
            (username, password)
        )
        admin = cursor.fetchone()

        conn.close()

        if admin:
            session["admin"] = username
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid Username or Password"

    return render_template("admin_login.html", error=error)

# ---------------- ADMIN SIGNUP ----------------
@app.route("/admin_signup", methods=["GET", "POST"])
def admin_signup():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM admins WHERE username=?", (username,))
        existing = cursor.fetchone()

        if existing:
            error = "Username already exists"
        else:
            cursor.execute(
                "INSERT INTO admins (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("admin_login"))

        conn.close()

    return render_template("admin_signup.html", error=error)

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    return render_template("admin_dashboard.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ---------------- STUDENT LOGIN ----------------
@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM student_users WHERE username=? AND password=?",
            (username, password)
        )
        student = cursor.fetchone()

        conn.close()

        if student:
            session["student"] = username
            return redirect(url_for("student_dashboard"))
        else:
            error = "Invalid Username or Password"

    return render_template("student_login.html", error=error)

# ---------------- STUDENT SIGNUP ----------------
@app.route("/student_signup", methods=["GET", "POST"])
def student_signup():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM student_users WHERE username=?",
            (username,)
        )
        existing = cursor.fetchone()

        if existing:
            error = "Username already exists"
        else:
            cursor.execute(
                "INSERT INTO student_users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("student_login"))

        conn.close()

    return render_template("student_signup.html", error=error)

# ---------------- STUDENT DASHBOARD ----------------
@app.route("/student")
def student_dashboard():
    if "student" not in session:
        return redirect(url_for("student_login"))
    return render_template("student_dashboard.html")

# ---------------- ADD STUDENT ----------------
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    error = None

    if request.method == "POST":
        roll_no = request.form["roll_no"].strip()
        name = request.form["name"].strip()
        marks = request.form["marks"]

        if not roll_no or not name or not marks:
            error = "All fields are required."
        else:
            try:
                marks = int(marks)

                if marks < 0 or marks > 100:
                    error = "Marks must be between 0 and 100."
                else:
                    if marks >= 90:
                        grade = "A"
                    elif marks >= 75:
                        grade = "B"
                    elif marks >= 60:
                        grade = "C"
                    elif marks >= 40:
                        grade = "D"
                    else:
                        grade = "F"

                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT * FROM students WHERE roll_no=?",
                        (roll_no,)
                    )
                    existing = cursor.fetchone()

                    if existing:
                        error = "Roll Number already exists."
                    else:
                        cursor.execute(
                            "INSERT INTO students (roll_no, name, marks, grade) VALUES (?, ?, ?, ?)",
                            (roll_no, name, marks, grade)
                        )
                        conn.commit()
                        conn.close()
                        return redirect(url_for("view_students"))

                    conn.close()

            except ValueError:
                error = "Marks must be a valid number."

    return render_template("add_student.html", error=error)

# ---------------- VIEW STUDENTS ----------------
@app.route("/view")
def view_students():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return render_template("view_students.html", students=students)

# ---------------- SEARCH (ADMIN) ----------------
@app.route("/admin_search", methods=["GET", "POST"])
def admin_search():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    student = None

    if request.method == "POST":
        search_value = request.form["search"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll_no=? OR name=?",
            (search_value, search_value)
        )
        student = cursor.fetchone()

        conn.close()

    return render_template("admin_search.html", student=student)

# ---------------- SEARCH (STUDENT) ----------------
@app.route("/student_search", methods=["GET", "POST"])
def student_search():
    if "student" not in session:
        return redirect(url_for("student_login"))

    student = None

    if request.method == "POST":
        search_value = request.form["search"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll_no=? OR name=?",
            (search_value, search_value)
        )
        student = cursor.fetchone()

        conn.close()

    return render_template("student_search.html", student=student)

# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete_student(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("view_students"))

# ---------------- EDIT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        name = request.form["name"]
        marks = request.form["marks"]
        grade = request.form["grade"]

        cursor.execute(
            "UPDATE students SET roll_no=?, name=?, marks=?, grade=? WHERE id=?",
            (roll_no, name, marks, grade, id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("view_students"))

    cursor.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cursor.fetchone()
    conn.close()

    return render_template("edit_student.html", student=student)

# ---------------- START APP ----------------
create_tables()

if __name__ == "__main__":
    app.run()