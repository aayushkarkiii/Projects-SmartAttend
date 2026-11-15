import os
import sqlite3
import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_recognition.db")


def get_connection():
    """Returns a SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables in the SQLite database if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Teachers / Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regteach (
            fname TEXT,
            lname TEXT,
            contact TEXT,
            email TEXT PRIMARY KEY,
            ssq TEXT,
            sa TEXT,
            pwd TEXT
        )
    """)

    # 2. Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student (
            Student_ID TEXT PRIMARY KEY,
            Name TEXT,
            Department TEXT,
            Course TEXT,
            Year TEXT,
            Semester TEXT,
            Division TEXT,
            Gender TEXT,
            DOB TEXT,
            Mobile_No TEXT,
            Address TEXT,
            Roll_No TEXT,
            Email TEXT,
            Teacher_Name TEXT,
            PhotoSample TEXT DEFAULT 'No'
        )
    """)

    # 3. Attendance Records Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stdattendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            std_id TEXT,
            std_roll_no TEXT,
            std_name TEXT,
            std_time TEXT,
            std_date TEXT,
            std_attendance TEXT DEFAULT 'Present'
        )
    """)

    # Create default demo teacher account if none exists
    cursor.execute("SELECT COUNT(*) FROM regteach")
    if cursor.fetchone()[0] == 0:
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@school.com")
        admin_pwd = os.environ.get("ADMIN_PASSWORD", "admin123")
        admin_contact = os.environ.get("ADMIN_CONTACT", "9800000000")
        cursor.execute("""
            INSERT INTO regteach (fname, lname, contact, email, ssq, sa, pwd)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("Admin", "Teacher", admin_contact, admin_email, "Your Pet Name", "Leo", admin_pwd))

    conn.commit()
    conn.close()


# ==================== Student Operations ====================

def get_all_students(search_query=None):
    conn = get_connection()
    cursor = conn.cursor()
    if search_query:
        query = "%" + search_query.strip() + "%"
        cursor.execute("""
            SELECT * FROM student 
            WHERE Student_ID LIKE ? OR Name LIKE ? OR Roll_No LIKE ? OR Department LIKE ?
            ORDER BY Student_ID ASC
        """, (query, query, query, query))
    else:
        cursor.execute("SELECT * FROM student ORDER BY Student_ID ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_by_id(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE Student_ID = ?", (str(student_id),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_student(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO student (
            Student_ID, Name, Department, Course, Year, Semester, 
            Division, Gender, DOB, Mobile_No, Address, Roll_No, 
            Email, Teacher_Name, PhotoSample
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(data.get("Student_ID")),
        data.get("Name"),
        data.get("Department"),
        data.get("Course"),
        data.get("Year"),
        data.get("Semester"),
        data.get("Division"),
        data.get("Gender"),
        data.get("DOB"),
        data.get("Mobile_No"),
        data.get("Address"),
        data.get("Roll_No"),
        data.get("Email"),
        data.get("Teacher_Name"),
        data.get("PhotoSample", "No")
    ))
    conn.commit()
    conn.close()


def update_student(student_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE student SET 
            Name = ?, Department = ?, Course = ?, Year = ?, 
            Semester = ?, Division = ?, Gender = ?, DOB = ?, 
            Mobile_No = ?, Address = ?, Roll_No = ?, Email = ?, 
            Teacher_Name = ?, PhotoSample = ?
        WHERE Student_ID = ?
    """, (
        data.get("Name"),
        data.get("Department"),
        data.get("Course"),
        data.get("Year"),
        data.get("Semester"),
        data.get("Division"),
        data.get("Gender"),
        data.get("DOB"),
        data.get("Mobile_No"),
        data.get("Address"),
        data.get("Roll_No"),
        data.get("Email"),
        data.get("Teacher_Name"),
        data.get("PhotoSample", "No"),
        str(student_id)
    ))
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM student WHERE Student_ID = ?", (str(student_id),))
    conn.commit()
    conn.close()


def update_photo_sample_status(student_id, status="Yes"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE student SET PhotoSample = ? WHERE Student_ID = ?", (status, str(student_id)))
    conn.commit()
    conn.close()


# ==================== Attendance Operations ====================

def mark_attendance_db(student_id, roll_no, name):
    """Marks attendance in SQLite database."""
    now = datetime.datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO stdattendance (std_id, std_roll_no, std_name, std_time, std_date, std_attendance)
        VALUES (?, ?, ?, ?, ?, 'Present')
    """, (str(student_id), str(roll_no), str(name), time_str, date_str))
    conn.commit()
    conn.close()


def get_attendance_records(date_filter=None):
    conn = get_connection()
    cursor = conn.cursor()
    if date_filter:
        cursor.execute("SELECT * FROM stdattendance WHERE std_date = ? ORDER BY id DESC", (date_filter,))
    else:
        cursor.execute("SELECT * FROM stdattendance ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_today_attendance():
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    return get_attendance_records(date_filter=today)


def clear_attendance_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stdattendance")
    conn.commit()
    conn.close()


# ==================== Auth Operations ====================

def get_teacher_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM regteach WHERE email = ?", (email.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def register_teacher(fname, lname, contact, email, ssq, sa, pwd):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO regteach (fname, lname, contact, email, ssq, sa, pwd)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (fname, lname, contact, email.strip(), ssq, sa, pwd))
    conn.commit()
    conn.close()


def reset_teacher_password(email, new_pwd):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE regteach SET pwd = ? WHERE email = ?", (new_pwd, email.strip()))
    conn.commit()
    conn.close()


# Initialize on import
init_db()
