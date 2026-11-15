from tkinter import *
from tkinter import ttk, messagebox
import time
from login import Login


class Startup:
    def __init__(self, root):
        self.root = root
        self.root.geometry("780x500+280+100")
        self.root.title("Smart Attendance System")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")
        self.root.focus_force()

        # Center Card
        card = Frame(self.root, bg="#1e293b", bd=1, relief="solid", padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center", width=620, height=380)

        title_lbl = Label(
            card,
            text="SMART ATTENDANCE SYSTEM",
            font=("Segoe UI", 22, "bold"),
            bg="#1e293b",
            fg="white"
        )
        title_lbl.pack(pady=(20, 8))

        subtitle_lbl = Label(
            card,
            text="Facial Recognition Attendance Management System",
            font=("Segoe UI", 12),
            bg="#1e293b",
            fg="#38bdf8"
        )
        subtitle_lbl.pack(pady=(0, 25))

        desc_lbl = Label(
            card,
            text="Automated Student Attendance, Face Recognition & Real-time Logging\nPowered by OpenCV & MySQL",
            font=("Segoe UI", 10),
            bg="#1e293b",
            fg="#94a3b8",
            justify="center"
        )
        desc_lbl.pack(pady=(0, 30))

        start_btn = Button(
            card,
            command=self.runn,
            text="Launch Application",
            font=("Segoe UI", 13, "bold"),
            bd=0,
            relief="flat",
            fg="white",
            bg="#2563eb",
            activeforeground="white",
            activebackground="#1d4ed8",
            cursor="hand2",
            height=2,
            width=26
        )
        start_btn.pack()

    def runn(self):
        self.root.withdraw()
        self.new_window = Toplevel(self.root)
        self.app = Login(self.new_window)

    def mainWindow(self):
        time.sleep(5)
        self.new_window = Toplevel(self.root)
        self.app = Login(self.new_window)


if __name__ == "__main__":
    root = Tk()
    obj = Startup(root)
    root.mainloop()
