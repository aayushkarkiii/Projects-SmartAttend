from tkinter import *
from PIL import Image, ImageTk
import os
import cv2
import numpy as np
from tkinter import messagebox

class Train:

    def __init__(self, root):
        self.root = root
        self.root.geometry("1366x768+0+0")
        self.root.title("Train Pannel")

        self.root.geometry("1100x700+130+50")
        self.root.title("Train Face Recognition Classifier")
        self.root.configure(bg="#f8fafc")

        # Header banner frame
        header_frame = Frame(self.root, bg="#1e3a8a", height=85)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        title_lb1 = Label(
            header_frame,
            text="TRAIN DATASET CLASSIFIER",
            font=("Segoe UI", 22, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title_lb1.pack(pady=(12, 2))

        subtitle_lb1 = Label(
            header_frame,
            text="Train LBPH Face Recognizer on Cropped Student Face Samples",
            font=("Segoe UI", 10),
            bg="#1e3a8a",
            fg="#bfdbfe"
        )
        subtitle_lb1.pack()

        # Center Card Container
        main_container = Frame(self.root, bg="#f8fafc")
        main_container.pack(expand=True, fill="both", padx=40, pady=40)

        card = Frame(main_container, bg="#ffffff", bd=1, relief="solid", padx=50, pady=40)
        card.pack(expand=True)

        card_title = Label(
            card,
            text="MODEL TRAINING ENGINE",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#c2410c"
        )
        card_title.pack(pady=(0, 10))

        info_lbl = Label(
            card,
            text="Click below to train the LBPH Face Recognizer on images in 'data_img/'.\nThe compiled classifier will be saved as 'coc.xml' for real-time recognition.",
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#475569",
            justify="center"
        )
        info_lbl.pack(pady=(0, 25))

        btn_train = Button(
            card,
            command=self.train_classifier,
            text="Train Dataset Now",
            font=("Segoe UI", 13, "bold"),
            bg="#c2410c",
            fg="white",
            activebackground="#9a3412",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            height=2,
            width=32
        )
        btn_train.pack(pady=(0, 20))

        hint_lbl = Label(
            card,
            text="Note: Ensure you have captured at least one student's photos via Student Panel before training.",
            font=("Segoe UI", 9, "italic"),
            bg="#ffffff",
            fg="#94a3b8"
        )
        hint_lbl.pack()

    # ==================Create Function of Training===================
    def train_classifier(self):
        data_dir = "data_img"
        path = [os.path.join(data_dir, file) for file in os.listdir(data_dir)]

        faces = []
        ids = []

        for image in path:
            img = Image.open(image).convert('L')  # convert to grayscale
            imageNp = np.array(img, 'uint8')
            id = int(os.path.split(image)[1].split('.')[1])

            faces.append(imageNp)
            ids.append(id)

            cv2.imshow("Training", imageNp)
            cv2.waitKey(1) == 13

        ids = np.array(ids)

        # =================Train Classifier=================
        clf = cv2.face_LBPHFaceRecognizer.create()
        clf.train(faces, ids)
        clf.save("coc.xml")

        cv2.destroyAllWindows()
        messagebox.showinfo("Result", "Training Dataset Completed!", parent=self.root)

    def Close(self):
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    obj = Train(root)
    root.mainloop()
