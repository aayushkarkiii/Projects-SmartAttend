from tkinter import *
from tkinter import ttk, messagebox
import os
import sys
import subprocess

from student import Student
from train import Train
from face_recognition import Face_Recognition
from attendance import Attendance
from developer import Developer


class Face_Recognition_System:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x780+130+30")
        self.root.title("Face Recognition Attendance System - Main Dashboard")
        self.root.configure(bg="#f8fafc")

        # ==================== Top Header Banner ====================
        header = Frame(self.root, bg="#1e3a8a", height=90)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title_lbl = Label(
            header,
            text="SMART ATTENDANCE SYSTEM",
            font=("Segoe UI", 24, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title_lbl.pack(pady=(12, 2))

        subtitle_lbl = Label(
            header,
            text="Facial Recognition Attendance Management System",
            font=("Segoe UI", 11),
            bg="#1e3a8a",
            fg="#bfdbfe"
        )
        subtitle_lbl.pack()

        # ==================== Main Series Panel Container ====================
        main_container = Frame(self.root, bg="#f8fafc")
        main_container.pack(expand=True, fill="both", padx=40, pady=20)

        # Central Card Panel
        card = Frame(main_container, bg="#ffffff", bd=1, relief="solid", padx=50, pady=25)
        card.pack(expand=True)

        card_title = Label(
            card,
            text="SYSTEM NAVIGATION PANEL",
            font=("Segoe UI", 15, "bold"),
            bg="#ffffff",
            fg="#1e3a8a"
        )
        card_title.pack(pady=(0, 6))

        card_subtitle = Label(
            card,
            text="Select an operation module from the series below:",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#64748b"
        )
        card_subtitle.pack(pady=(0, 18))

        # ==================== Buttons in Straight Series ====================
        btn_style = {
            "font": ("Segoe UI", 12, "bold"),
            "width": 38,
            "height": 2,
            "bd": 0,
            "cursor": "hand2",
            "relief": "flat"
        }

        # 1. Student Panel
        self.btn_student = Button(
            card,
            text="1.  Student Management Panel",
            command=self.student_pannels,
            bg="#1e40af",
            fg="white",
            activebackground="#1e3a8a",
            activeforeground="white",
            **btn_style
        )
        self.btn_student.pack(pady=5)

        # 2. Face Detector (Webcam Recognition)
        self.btn_detector = Button(
            card,
            text="2.  Face Recognition & Attendance",
            command=self.face_rec,
            bg="#047857",
            fg="white",
            activebackground="#065f46",
            activeforeground="white",
            **btn_style
        )
        self.btn_detector.pack(pady=5)

        # 3. Attendance Records & CSV Export
        self.btn_attendance = Button(
            card,
            text="3.  Attendance Records & Logs",
            command=self.attendance_pannel,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            **btn_style
        )
        self.btn_attendance.pack(pady=5)

        # 4. Train Face Classifier
        self.btn_train = Button(
            card,
            text="4.  Train Face Recognition Model",
            command=self.train_pannels,
            bg="#c2410c",
            fg="white",
            activebackground="#9a3412",
            activeforeground="white",
            **btn_style
        )
        self.btn_train.pack(pady=5)

        # 5. Photos / Dataset Folder
        self.btn_photos = Button(
            card,
            text="5.  Open Sample Photos Dataset",
            command=self.open_img,
            bg="#6d28d9",
            fg="white",
            activebackground="#5b21b6",
            activeforeground="white",
            **btn_style
        )
        self.btn_photos.pack(pady=5)

        # 6. Developers
        self.btn_developer = Button(
            card,
            text="6.  Developer Information",
            command=self.developr,
            bg="#475569",
            fg="white",
            activebackground="#334155",
            activeforeground="white",
            **btn_style
        )
        self.btn_developer.pack(pady=5)

        # 7. Exit Application
        self.btn_exit = Button(
            card,
            text="7.  Exit Application",
            command=self.Close,
            bg="#dc2626",
            fg="white",
            activebackground="#b91c1c",
            activeforeground="white",
            **btn_style
        )
        self.btn_exit.pack(pady=5)

        # ==================== Bottom Footer Status Bar ====================
        footer = Frame(self.root, bg="#e2e8f0", height=30)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        status_lbl = Label(
            footer,
            text="Status: System Ready | Python 3.12 | OpenCV LBPH Powered",
            font=("Segoe UI", 9),
            bg="#e2e8f0",
            fg="#475569"
        )
        status_lbl.pack(side="left", padx=15)

    # ==================== Function for Open Images Folder ====================
    def open_img(self):
        data_dir = "data_img"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        try:
            if sys.platform.startswith("win"):
                os.startfile(data_dir)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", data_dir])
            else:
                subprocess.Popen(["xdg-open", data_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}", parent=self.root)

    # ==================== Navigation Functions ====================
    def student_pannels(self):
        self.new_window = Toplevel(self.root)
        self.app = Student(self.new_window)

    def train_pannels(self):
        self.new_window = Toplevel(self.root)
        self.app = Train(self.new_window)

    def face_rec(self):
        self.new_window = Toplevel(self.root)
        self.app = Face_Recognition(self.new_window)

    def attendance_pannel(self):
        self.new_window = Toplevel(self.root)
        self.app = Attendance(self.new_window)

    def developr(self):
        self.new_window = Toplevel(self.root)
        self.app = Developer(self.new_window)

    def Close(self):
        self.root.destroy()


if __name__ == "__main__":
    root = Tk()
    obj = Face_Recognition_System(root)
    root.mainloop()
