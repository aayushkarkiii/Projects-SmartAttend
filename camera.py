import os
import cv2
import time
import datetime
import numpy as np
from PIL import Image
import database

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CASCADE_PATH = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
MODEL_PATH = os.path.join(BASE_DIR, "coc.xml")
DATA_DIR = os.path.join(BASE_DIR, "data_img")
CSV_PATH = os.path.join(BASE_DIR, "attendance.csv")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# Debounce tracking: {student_id: timestamp_of_last_mark}
recent_marks = {}
# Recent attendance feed for web polling
recent_attendees = []


def get_cached_students():
    """Cache student records in memory to eliminate per-frame SQL queries."""
    students = database.get_all_students()
    return {str(s["Student_ID"]): s for s in students}


def log_attendance(student_id, roll_no, name):
    """Logs attendance to both CSV and Database with debouncing (5 min cooldown)."""
    now = datetime.datetime.now()
    now_ts = time.time()

    # Debounce check: don't re-log if marked within last 300 seconds (5 mins)
    if student_id in recent_marks and (now_ts - recent_marks[student_id]) < 300:
        return False

    recent_marks[student_id] = now_ts
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%H:%M:%S")

    # 1. Append to CSV
    try:
        with open(CSV_PATH, "a+", newline="\n") as f:
            f.seek(0, 2)
            if f.tell() == 0:
                f.write("std_id,std_roll_no,std_name,std_time,std_date,std_attendance\n")
            f.write(f"{student_id},{roll_no},{name},{time_str},{date_str},Present\n")
    except Exception as e:
        print(f"Error appending to CSV: {e}")

    # 2. Insert into Database
    try:
        database.mark_attendance_db(student_id, roll_no, name)
    except Exception as e:
        print(f"Error writing to database: {e}")

    # 3. Add to live notification feed
    recent_attendees.insert(0, {
        "student_id": student_id,
        "roll_no": roll_no,
        "name": name,
        "time": time_str,
        "date": date_str
    })
    if len(recent_attendees) > 20:
        recent_attendees.pop()

    return True


class VideoStreamManager:
    """Manages OpenCV VideoCapture stream safely."""
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)
        return self.cap.isOpened()

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
            if not self.start():
                return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            self.cap = None


def generate_placeholder_frame(message="Camera Not Found / Busy"):
    """Generates an image frame with an error/status message when camera is unavailable."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (30, 41, 59)  # Dark slate background
    cv2.putText(frame, message, (60, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (239, 68, 68), 2)
    cv2.putText(frame, "Check camera connection & permissions", (80, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (148, 163, 184), 1)
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()


def generate_detector_stream():
    """Generator for live webcam face detection & attendance marking."""
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    
    # Load recognizer if trained model exists
    recognizer = None
    if os.path.exists(MODEL_PATH):
        try:
            recognizer = cv2.face_LBPHFaceRecognizer.create()
            recognizer.read(MODEL_PATH)
        except Exception as e:
            print(f"Error loading classifier: {e}")
            recognizer = None

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        placeholder = generate_placeholder_frame("Webcam unavailable (Device 0)")
        while True:
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + placeholder + b'\r\n')
            time.sleep(1)

    students_cache = get_cached_students()
    last_cache_refresh = time.time()

    try:
        while True:
            # Refresh student cache periodically (every 30s)
            if time.time() - last_cache_refresh > 30:
                students_cache = get_cached_students()
                last_cache_refresh = time.time()

            ret, frame = camera.read()
            if not ret:
                time.sleep(0.05)
                continue

            # Mirror frame for natural webcam experience
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

            for (x, y, w, h) in faces:
                if recognizer is not None:
                    face_roi = gray[y:y+h, x:x+w]
                    try:
                        pred_id, dist = recognizer.predict(face_roi)
                        # LBPH distance: lower is better. Convert distance to confidence %
                        confidence = int(100 * (1 - dist / 300))
                    except Exception:
                        confidence = 0
                        pred_id = -1

                    if confidence > 50 and str(pred_id) in students_cache:
                        student = students_cache[str(pred_id)]
                        name = student.get("Name", "Student")
                        roll = student.get("Roll_No", str(pred_id))
                        
                        # Log attendance (debounced)
                        log_attendance(str(pred_id), roll, name)

                        # Draw green box
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (34, 197, 94), 2)
                        cv2.rectangle(frame, (x, y-60), (x+w, y), (34, 197, 94), cv2.FILLED)
                        cv2.putText(frame, f"{name} ({confidence}%)", (x+6, y-36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        cv2.putText(frame, f"ID: {pred_id} | Roll: {roll}", (x+6, y-12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    else:
                        # Unknown face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (239, 68, 68), 2)
                        cv2.rectangle(frame, (x, y-30), (x+w, y), (239, 68, 68), cv2.FILLED)
                        cv2.putText(frame, "Unknown Face", (x+6, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                else:
                    # Model not yet trained: detect only
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (59, 130, 246), 2)
                    cv2.putText(frame, "Face Detected (Model Not Trained)", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (59, 130, 246), 1)

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        camera.release()


def generate_capture_stream(student_id):
    """Generator for streaming webcam while capturing 100 face samples for student."""
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        placeholder = generate_placeholder_frame("Webcam unavailable (Device 0)")
        while True:
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + placeholder + b'\r\n')
            time.sleep(1)

    count = 0
    max_samples = 100

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                time.sleep(0.05)
                continue

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))

            for (x, y, w, h) in faces:
                if count < max_samples:
                    count += 1
                    crop = gray[y:y+h, x:x+w]
                    crop_resized = cv2.resize(crop, (200, 200))
                    file_path = os.path.join(DATA_DIR, f"user.{student_id}.{count}.jpg")
                    cv2.imwrite(file_path, crop_resized)

                    cv2.rectangle(frame, (x, y), (x+w, y+h), (59, 130, 246), 2)
                    cv2.putText(frame, f"Capturing: {count}/{max_samples}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (59, 130, 246), 2)
                else:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (34, 197, 94), 2)
                    cv2.putText(frame, "Capture Complete! (100/100)", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (34, 197, 94), 2)

            # If done, update database status
            if count >= max_samples:
                database.update_photo_sample_status(student_id, "Yes")
                cv2.putText(frame, "SUCCESS: 100 samples captured!", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (34, 197, 94), 2)

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            if count >= max_samples:
                time.sleep(0.1)
    finally:
        camera.release()


def train_classifier():
    """Trains the LBPH recognizer model on all images in data_img/."""
    image_paths = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if not image_paths:
        return {"status": "error", "message": "No sample images found in 'data_img/'. Please capture student photos first."}

    faces = []
    ids = []

    for img_path in image_paths:
        try:
            filename = os.path.basename(img_path)
            parts = filename.split('.')
            if len(parts) >= 3 and parts[0] == "user":
                student_id = int(parts[1])
                pil_img = Image.open(img_path).convert('L')
                img_np = np.array(pil_img, 'uint8')
                faces.append(img_np)
                ids.append(student_id)
        except Exception as e:
            print(f"Skipping corrupted image {img_path}: {e}")
            continue

    if not faces or not ids:
        return {"status": "error", "message": "Could not parse student face samples. Verify image filenames."}

    try:
        clf = cv2.face_LBPHFaceRecognizer.create()
        clf.train(faces, np.array(ids))
        clf.save(MODEL_PATH)
        return {
            "status": "success",
            "message": f"Model successfully trained on {len(faces)} images across {len(set(ids))} students!",
            "samples_count": len(faces),
            "students_count": len(set(ids))
        }
    except Exception as e:
        return {"status": "error", "message": f"Training failed: {e}"}
