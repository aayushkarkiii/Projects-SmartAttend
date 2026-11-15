from sys import path
from tkinter import*
from tkinter import ttk
from PIL import Image,ImageTk
import os
import mysql.connector
import cv2
import numpy as np
from tkinter import messagebox
from time import strftime
from datetime import datetime
import face_recognition
class Face_Recognition:

    def __init__(self,root):
        self.root=root
        self.root.geometry("1100x700+130+50")
        self.root.title("Face Recognition & Attendance Detection")
        self.root.configure(bg="#f8fafc")

        # Header banner frame
        header_frame = Frame(self.root, bg="#1e3a8a", height=85)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        title_lb1 = Label(
            header_frame,
            text="LIVE FACE RECOGNITION SYSTEM",
            font=("Segoe UI", 22, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title_lb1.pack(pady=(12, 2))

        subtitle_lb1 = Label(
            header_frame,
            text="Real-Time Webcam Face Verification & Automated Attendance Logging",
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
            text="CAMERA DETECTOR MODULE",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#047857"
        )
        card_title.pack(pady=(0, 10))

        info_lbl = Label(
            card,
            text="Click below to open webcam and detect student faces.\nRecognized students will be marked Present in attendance.csv and MySQL.",
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#475569",
            justify="center"
        )
        info_lbl.pack(pady=(0, 25))

        btn_detect = Button(
            card,
            command=self.face_recog,
            text="Launch Face Detector (Webcam)",
            font=("Segoe UI", 13, "bold"),
            bg="#047857",
            fg="white",
            activebackground="#065f46",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            height=2,
            width=32
        )
        btn_detect.pack(pady=(0, 20))

        hint_lbl = Label(
            card,
            text="Tip: While camera window is active, press Enter to close the stream.",
            font=("Segoe UI", 9, "italic"),
            bg="#ffffff",
            fg="#94a3b8"
        )
        hint_lbl.pack()
    

    def mark_attendance(self,i,r,n):
        with open("attendance.csv","a+",newline="\n") as f:
            now=datetime.now()
            d1=now.strftime("%d/%m/%Y")
            dtString=now.strftime("%H:%M:%S")
            f.writelines(f"\n{i}, {r}, {n}, {dtString}, {d1}, Present")


    def face_recog(self):
        faceCascade=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        clf = cv2.face_LBPHFaceRecognizer.create()
        print("Loading the recognizer model...")
        try:
            clf.read("coc.xml")
            print("Recognizer model loaded successfully.")
        except cv2.error as e:
            print(f"Error loading recognizer model: {e}")

        videoCap=cv2.VideoCapture(0)

        while True:
            ret,img=videoCap.read()
            gray_image=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            featuers=faceCascade.detectMultiScale(gray_image,1.1,10)

            for (x,y,w,h) in featuers:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3)
                id,predict=clf.predict(gray_image[y:y+h,x:x+w])

                confidence=int((100*(1-predict/300)))

                # threshold = 50 

                conn = mysql.connector.connect(user='root', password='admin',host='localhost',database='face_recognition',port=3306)
                cursor = conn.cursor()

                cursor.execute("select Name from student where Student_ID="+str(id))
                n=cursor.fetchone()
                


            # n = n[0] if n else "Unknown"
                # n="+".join(n)

                cursor.execute("select Roll_No from student where Student_ID="+str(id))
                r=cursor.fetchone()

                
                # r = r[0] if r else "Unknown"
                # r="+".join(r)

                
               

                cursor.execute("select Student_ID from student where Student_ID="+str(id))
                i=cursor.fetchone()

                # i= i[0] if i else "Unknown"

                # i= "+".join(i)
                


                if confidence > 50 :
                    cv2.putText(img,f"Student_ID:{i}",(x,y-80),cv2.FONT_HERSHEY_COMPLEX,0.8,(64,15,223),2)
                    cv2.putText(img,f"Name:{n}",(x,y-55),cv2.FONT_HERSHEY_COMPLEX,0.8,(64,15,223),2)
                    cv2.putText(img,f"Roll-No:{r}",(x,y-30),cv2.FONT_HERSHEY_COMPLEX,0.8,(64,15,223),2)
                    self.mark_attendance(i,r,n)
                else:
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),3)
                    cv2.putText(img,"Unknown Face",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,0),3)    

            cv2.imshow("Face Detector",img)

            if cv2.waitKey(1) == 13:
                break
        videoCap.release()
        cv2.destroyAllWindows()




if __name__ == "__main__":
    root=Tk()
    obj=Face_Recognition(root)
    root.mainloop()





