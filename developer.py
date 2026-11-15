from tkinter import *
from tkinter import ttk


class Developer:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x700+130+50")
        self.root.title("Developer Information & Credits")
        self.root.configure(bg="#f8fafc")

        # Header banner frame
        header_frame = Frame(self.root, bg="#1e3a8a", height=85)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        title_lb1 = Label(
            header_frame,
            text="PROJECT DEVELOPERS & CONTRIBUTORS",
            font=("Segoe UI", 22, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title_lb1.pack(pady=(12, 2))

        subtitle_lb1 = Label(
            header_frame,
            text="Smart Face Recognition Attendance System Engineering Team",
            font=("Segoe UI", 10),
            bg="#1e3a8a",
            fg="#bfdbfe"
        )
        subtitle_lb1.pack()

        # Center Container
        main_container = Frame(self.root, bg="#f8fafc")
        main_container.pack(expand=True, fill="both", padx=50, pady=40)

        card = Frame(main_container, bg="#ffffff", bd=1, relief="solid", padx=40, pady=30)
        card.pack(expand=True)

        card_title = Label(
            card,
            text="CORE DEVELOPMENT TEAM",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#1e3a8a"
        )
        card_title.pack(pady=(0, 25))

        # Developers Container
        devs_frame = Frame(card, bg="#ffffff")
        devs_frame.pack()

        devs = [
            ("Aayush Karki", "Lead Developer / ML & Architecture", "#2563eb"),
            ("Basanta Bist", "Core Developer / Backend & Database", "#059669"),
            ("Keshav Dahal", "Core Developer / GUI & Integration", "#0284c7")
        ]

        for name, role, color in devs:
            dev_box = Frame(devs_frame, bg="#f1f5f9", bd=1, relief="solid", padx=20, pady=20, width=240, height=180)
            dev_box.pack(side="left", padx=15)
            dev_box.pack_propagate(False)

            # Avatar placeholder badge
            initials = "".join([part[0] for part in name.split()])
            badge = Label(
                dev_box,
                text=initials,
                font=("Segoe UI", 16, "bold"),
                bg=color,
                fg="white",
                width=4,
                height=2
            )
            badge.pack(pady=(5, 10))

            name_lbl = Label(
                dev_box,
                text=name,
                font=("Segoe UI", 13, "bold"),
                bg="#f1f5f9",
                fg="#0f172a"
            )
            name_lbl.pack()

            role_lbl = Label(
                dev_box,
                text=role,
                font=("Segoe UI", 9),
                bg="#f1f5f9",
                fg="#64748b",
                wraplength=210,
                justify="center"
            )
            role_lbl.pack(pady=(4, 0))

        # Project Info section
        info_frame = Frame(card, bg="#f8fafc", bd=1, relief="solid", padx=20, pady=12)
        info_frame.pack(fill="x", pady=(30, 0))

        info_text = Label(
            info_frame,
            text="Technologies: Python 3.12 | OpenCV LBPH | Tkinter | MySQL Database",
            font=("Segoe UI", 10, "bold"),
            bg="#f8fafc",
            fg="#475569"
        )
        info_text.pack()


if __name__ == "__main__":
    root = Tk()
    obj = Developer(root)
    root.mainloop()
