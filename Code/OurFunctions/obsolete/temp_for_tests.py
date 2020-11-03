import PIL
from PIL import Image, ImageTk
import cv2
from tkinter import *
width, height = 800, 600
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

root = Tk()
root.bind('<Escape>', lambda e: root.quit())

#Create the main Frame -----------------------------------------------------------------
FrmMain = Frame(root)
LblImg1 = Label(FrmMain, text = "Picture 1",   anchor=W, width=800, bg="light sky blue")
LblImg2 = Label(FrmMain, text = "Picture 2",   anchor=W, width=800, bg="light sky blue")

LblImg1.grid (row=2, rowspan = 3, column=1, columnspan=3);
LblImg2.grid (row=2, rowspan = 3, column=4, columnspan=3);

FrmMain.pack()

def show_frame():
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = PIL.Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    LblImg1.imgtk = imgtk
    LblImg1.configure(image=imgtk)
    LblImg1.after(10, show_frame)

    frame2 = cv2.flip(frame, 1)
    cv2image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGBA)
    img2 = PIL.Image.fromarray(cv2image2)
    imgtk2 = ImageTk.PhotoImage(image=img2)
    LblImg2.imgtk = imgtk2
    LblImg2.configure(image=imgtk2)
    # LblImg2.after(10, show_frame)

show_frame()
root.mainloop()