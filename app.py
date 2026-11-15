import os
import functools
from flask import (
    Flask, render_template, request, redirect, url_for, 
    session, flash, jsonify, Response, send_file
)
import database
import camera

app = Flask(__name__)
app.secret_key = os.urandom(24)


def login_required(view):
    """Decorator to require teacher login for protected routes."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "user_email" not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view


# ==================== Authentication Routes ====================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pwd = request.form.get("password", "")

        teacher = database.get_teacher_by_email(email)
        if teacher and teacher.get("pwd") == pwd:
            session["user_email"] = teacher["email"]
            session["user_name"] = f"{teacher.get('fname', '')} {teacher.get('lname', '')}".strip()
            flash(f"Welcome back, {session['user_name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fname = request.form.get("fname", "").strip()
        lname = request.form.get("lname", "").strip()
        contact = request.form.get("contact", "").strip()
        email = request.form.get("email", "").strip()
        ssq = request.form.get("ssq", "")
        sa = request.form.get("sa", "").strip()
        pwd = request.form.get("pwd", "")
        cpwd = request.form.get("cpwd", "")

        if not email or not pwd:
            flash("Email and password are required.", "danger")
        elif pwd != cpwd:
            flash("Passwords do not match.", "danger")
        elif database.get_teacher_by_email(email):
            flash("An account with this email already exists.", "warning")
        else:
            try:
                database.register_teacher(fname, lname, contact, email, ssq, sa, pwd)
                flash("Registration successful! You may now sign in.", "success")
                return redirect(url_for("login"))
            except Exception as e:
                flash(f"Registration failed: {e}", "danger")

    return render_template("register.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        sa = request.form.get("sa", "").strip()
        new_pwd = request.form.get("new_pwd", "")

        teacher = database.get_teacher_by_email(email)
        if not teacher:
            flash("Account with this email was not found.", "danger")
        elif teacher.get("sa", "").strip().lower() != sa.lower():
            flash("Security question answer does not match.", "danger")
        else:
            database.reset_teacher_password(email, new_pwd)
            flash("Password reset successfully! Please sign in with your new password.", "success")
            return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))


# ==================== Dashboard ====================

@app.route("/")
@login_required
def dashboard():
    students = database.get_all_students()
    today_records = database.get_today_attendance()
    all_records = database.get_attendance_records()

    # Image sample stats
    sample_images = [f for f in os.listdir(camera.DATA_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
    model_exists = os.path.exists(camera.MODEL_PATH)
    model_time = None
    if model_exists:
        mtime = os.path.getmtime(camera.MODEL_PATH)
        import datetime
        model_time = datetime.datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M")

    return render_template(
        "dashboard.html",
        total_students=len(students),
        today_attendance=len(today_records),
        total_attendance=len(all_records),
        total_samples=len(sample_images),
        model_exists=model_exists,
        model_time=model_time,
        recent_records=today_records[:10]
    )


# ==================== Students Management ====================

@app.route("/students")
@login_required
def students():
    search = request.args.get("search", "").strip()
    student_list = database.get_all_students(search_query=search if search else None)
    return render_template("students.html", students=student_list, search=search)


@app.route("/students/add", methods=["POST"])
@login_required
def add_student():
    data = {
        "Student_ID": request.form.get("Student_ID", "").strip(),
        "Name": request.form.get("Name", "").strip(),
        "Department": request.form.get("Department", ""),
        "Course": request.form.get("Course", ""),
        "Year": request.form.get("Year", ""),
        "Semester": request.form.get("Semester", ""),
        "Division": request.form.get("Division", ""),
        "Gender": request.form.get("Gender", ""),
        "DOB": request.form.get("DOB", ""),
        "Mobile_No": request.form.get("Mobile_No", ""),
        "Address": request.form.get("Address", ""),
        "Roll_No": request.form.get("Roll_No", ""),
        "Email": request.form.get("Email", ""),
        "Teacher_Name": session.get("user_name", "Teacher"),
        "PhotoSample": "No"
    }

    if not data["Student_ID"] or not data["Name"]:
        flash("Student ID and Name are required.", "danger")
        return redirect(url_for("students"))

    if database.get_student_by_id(data["Student_ID"]):
        flash(f"Student ID '{data['Student_ID']}' already exists.", "warning")
        return redirect(url_for("students"))

    try:
        database.add_student(data)
        flash(f"Student '{data['Name']}' added successfully!", "success")
    except Exception as e:
        flash(f"Failed to add student: {e}", "danger")

    return redirect(url_for("students"))


@app.route("/students/edit/<student_id>", methods=["POST"])
@login_required
def edit_student(student_id):
    student = database.get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("students"))

    data = {
        "Name": request.form.get("Name", student["Name"]),
        "Department": request.form.get("Department", student["Department"]),
        "Course": request.form.get("Course", student["Course"]),
        "Year": request.form.get("Year", student["Year"]),
        "Semester": request.form.get("Semester", student["Semester"]),
        "Division": request.form.get("Division", student["Division"]),
        "Gender": request.form.get("Gender", student["Gender"]),
        "DOB": request.form.get("DOB", student["DOB"]),
        "Mobile_No": request.form.get("Mobile_No", student["Mobile_No"]),
        "Address": request.form.get("Address", student["Address"]),
        "Roll_No": request.form.get("Roll_No", student["Roll_No"]),
        "Email": request.form.get("Email", student["Email"]),
        "Teacher_Name": request.form.get("Teacher_Name", student["Teacher_Name"]),
        "PhotoSample": student.get("PhotoSample", "No")
    }

    try:
        database.update_student(student_id, data)
        flash(f"Student '{data['Name']}' updated successfully.", "success")
    except Exception as e:
        flash(f"Update failed: {e}", "danger")

    return redirect(url_for("students"))


@app.route("/students/delete/<student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    try:
        database.delete_student(student_id)
        # Delete associated sample images
        prefix = f"user.{student_id}."
        for f in os.listdir(camera.DATA_DIR):
            if f.startswith(prefix):
                try:
                    os.remove(os.path.join(camera.DATA_DIR, f))
                except Exception:
                    pass
        flash(f"Student ID '{student_id}' and photo samples deleted.", "info")
    except Exception as e:
        flash(f"Deletion failed: {e}", "danger")

    return redirect(url_for("students"))


@app.route("/students/capture/<student_id>")
@login_required
def capture_student_photos(student_id):
    student = database.get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("students"))
    return render_template("capture.html", student=student)


# ==================== Live Video Feeds ====================

@app.route("/video_feed/detector")
@login_required
def video_feed_detector():
    return Response(
        camera.generate_detector_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/video_feed/capture/<student_id>")
@login_required
def video_feed_capture(student_id):
    return Response(
        camera.generate_capture_stream(student_id),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ==================== Attendance Detector & Real-Time View ====================

@app.route("/detector")
@login_required
def detector():
    model_exists = os.path.exists(camera.MODEL_PATH)
    return render_template("detector.html", model_exists=model_exists)


@app.route("/api/recent_attendees")
@login_required
def api_recent_attendees():
    return jsonify(camera.recent_attendees)


# ==================== Model Training ====================

@app.route("/train")
@login_required
def train_page():
    images = [f for f in os.listdir(camera.DATA_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
    unique_ids = set()
    for img in images:
        parts = img.split('.')
        if len(parts) >= 3 and parts[0] == "user":
            unique_ids.add(parts[1])

    model_exists = os.path.exists(camera.MODEL_PATH)
    model_info = None
    if model_exists:
        mtime = os.path.getmtime(camera.MODEL_PATH)
        size = os.path.getsize(camera.MODEL_PATH)
        import datetime
        model_info = {
            "mtime": datetime.datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S"),
            "size_kb": round(size / 1024, 1)
        }

    return render_template(
        "train.html",
        total_images=len(images),
        students_represented=len(unique_ids),
        model_exists=model_exists,
        model_info=model_info
    )


@app.route("/api/train", methods=["POST"])
@login_required
def api_train():
    result = camera.train_classifier()
    return jsonify(result)


# ==================== Attendance Records ====================

@app.route("/attendance")
@login_required
def attendance():
    date_filter = request.args.get("date", "").strip()
    records = database.get_attendance_records(date_filter=date_filter if date_filter else None)
    return render_template("attendance.html", records=records, date_filter=date_filter)


@app.route("/attendance/export")
@login_required
def export_attendance():
    if os.path.exists(camera.CSV_PATH):
        return send_file(
            camera.CSV_PATH,
            as_attachment=True,
            download_name=f"attendance_export.csv",
            mimetype="text/csv"
        )
    else:
        flash("No attendance records found to export.", "warning")
        return redirect(url_for("attendance"))


@app.route("/attendance/clear", methods=["POST"])
@login_required
def clear_attendance():
    try:
        database.clear_attendance_records()
        if os.path.exists(camera.CSV_PATH):
            with open(camera.CSV_PATH, "w") as f:
                f.write("std_id,std_roll_no,std_name,std_time,std_date,std_attendance\n")
        flash("All attendance records have been cleared.", "info")
    except Exception as e:
        flash(f"Failed to clear attendance: {e}", "danger")
    return redirect(url_for("attendance"))


# ==================== Developers Page ====================

@app.route("/developers")
@login_required
def developers():
    return render_template("developers.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
