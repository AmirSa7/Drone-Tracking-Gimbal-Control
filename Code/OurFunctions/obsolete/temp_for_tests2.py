from tkinter import *
from random import randint

# these two imports are important 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time

def data_points():
    f = open("data.txt", "w")
    for i in range(10):
        f.write(str(randint(0, 10)) + '\n')
    f.close()

    f = open("data.txt", "r")
    data = f.readlines()
    f.close()

    l = []
    for i in range(len(data)):
        l.append(int(data[i].rstrip("\n")))
    print(l)
    return l


def app():

    def plotter():
        while True:
            ax.cla()
            ax.grid()
            dpts = data_points()
            ax.plot(range(10), dpts, marker='o', color='orange')
            graph.draw()
            time.sleep(1)


    # initialise a window. 
    root = Tk()
    root.bind('<Escape>', lambda e: root.quit())
    root.config(background='white')
    root.geometry("1000x700")

    lab = Label(root, text="Live Plotting", bg='white').pack()

    fig = Figure()

    ax = fig.add_subplot(111)
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.grid()

    graph = FigureCanvasTkAgg(fig, master=root)
    graph.get_tk_widget().pack(side="top", fill='both', expand=True)

    plotter()
    root.mainloop()


if __name__ == '__main__':
    app()