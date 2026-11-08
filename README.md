# Face Attendance System

A desktop attendance management app that uses face recognition to mark students present. Built with Python, Tkinter, OpenCV, and MySQL.

The idea is simple — register students, capture their face photos, train a recognizer model, and then let the system automatically identify them via webcam and log attendance.

## How it works

1. **Register/Login** — Teachers register with email and password. Login opens the main dashboard.
2. **Add Students** — Enter student details (name, roll number, department, etc.) through the Student Panel.
3. **Capture Faces** — Take 100 face samples per student using the webcam. Images are saved as grayscale crops in `data_img/`.
4. **Train Model** — Train an LBPH (Local Binary Patterns Histogram) face recognizer on the captured images. The trained model is saved as `coc.xml`.
5. **Detect & Mark Attendance** — Run face detection via webcam. Recognized faces are matched against the database and attendance is logged to `attendance.csv` with timestamp.
6. **View/Export Attendance** — Import or export attendance records as CSV. Attendance is also stored in MySQL for persistence.

## Project structure

```
├── loading.py            # Splash/startup screen
├── login.py              # Login window + password reset
├── register.py           # Teacher registration
├── main.py               # Main dashboard (standalone entry)
├── student.py            # Student CRUD panel
├── train.py              # Train the face recognizer
├── face_recognition.py   # Webcam face detection + attendance marking
├── attendance.py         # View, import/export attendance records
├── developer.py          # Developer credits page
├── databaseTest.py       # Quick script to test MySQL connection
├── haarcascade_frontalface_default.xml  # OpenCV Haar cascade for face detection
├── attendance.csv        # Attendance log (auto-generated)
└── data_img/             # Face sample images (created at runtime)
```

## Prerequisites

- Python 3.x
- MySQL server running locally
- A webcam

## Setup

### 1. Install Python packages

```bash
pip install opencv-contrib-python numpy pillow mysql-connector-python
```

`opencv-contrib-python` is needed (not just `opencv-python`) because the LBPH face recognizer lives in the contrib modules.

### 2. Set up the MySQL database

Connect to your MySQL server and run:

```sql
CREATE DATABASE face_recognition;
USE face_recognition;

CREATE TABLE student (
    Student_ID VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(100),
    Department VARCHAR(100),
    Course VARCHAR(100),
    Year VARCHAR(20),
    Semester VARCHAR(20),
    Division VARCHAR(20),
    Gender VARCHAR(10),
    DOB VARCHAR(20),
    Mobile_No VARCHAR(15),
    Address VARCHAR(200),
    Roll_No VARCHAR(20),
    Email VARCHAR(100),
    Teacher_Name VARCHAR(100),
    PhotoSample VARCHAR(10)
);

CREATE TABLE regteach (
    fname VARCHAR(100),
    lname VARCHAR(100),
    contact VARCHAR(15),
    email VARCHAR(100) PRIMARY KEY,
    ssq VARCHAR(100),
    sa VARCHAR(100),
    pwd VARCHAR(100)
);

CREATE TABLE stdattendance (
    std_id VARCHAR(20),
    std_roll_no VARCHAR(20),
    std_name VARCHAR(100),
    std_time VARCHAR(20),
    std_date VARCHAR(20),
    std_attendance VARCHAR(20)
);
```

### 3. Update database credentials

The code connects to MySQL with `user='root'` and `password='admin'` on `localhost:3306`. If yours are different, update the connection strings in the Python files.

### 4. Download required XML files

Download `clf.xml` and `coc.xml` (pre-trained recognizer models) from:

**https://mega.nz/folder/Py4FTKjZ#Y3xzOdi6R1Rohq7pVXFRUA**

Place both files in the project root directory. (You can also generate `coc.xml` yourself by training — see below.)

### 5. Update image paths

The GUI loads banner/background images from hardcoded Windows paths (e.g., `S:\Project-II\Images_GUI\...`). You'll need to either:
- Create an `Images_GUI` folder with your own images and update the paths in the code, or
- Comment out the image-loading lines if you just want it to run

### 6. Create the dataset folder

```bash
mkdir data_img
```

## Running

Start from the loading screen:

```bash
python loading.py
```

Or jump straight to the login:

```bash
python login.py
```

Or skip auth entirely and open the main dashboard:

```bash
python main.py
```

### Taking attendance

1. Open **Student Panel** → fill in student details → click **Take Pic**
2. The webcam opens and captures 100 face samples automatically. Press Enter to stop early.
3. Go to **Data Train** → click **Train Dataset**. Wait for it to finish.
4. Go to **Face Detector** → click **Face Detector**. The webcam opens and identifies registered faces in real time. Press Enter to close.
5. Check `attendance.csv` or the **Attendance** panel for records.

## Built with

- **Tkinter** — GUI
- **OpenCV** — Face detection (Haar cascades) and recognition (LBPH)
- **MySQL** — Student records and attendance storage
- **Pillow** — Image handling for the GUI

## Developers

- Aayush Karki
- Basanta Bist
- Keshav Dahal

## License

MIT — see [LICENSE](LICENSE) for details.
