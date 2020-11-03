from tkinter import *
from tkinter import font
import time
import cv2
import PIL
from PIL import ImageTk
import matplotlib
matplotlib.use('Agg')
from OurFunctions.helpers import DataHolder

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation


class Gui:
    def __init__(self, zoom_frame_queue, wide_frame_queue, graph_data_queue, graph_diff_queue, window_title):
        # parameters
        self.main_bg = '#143e63'
        # thread queues
        self.zoom_frame_queue = zoom_frame_queue
        self.wide_frame_queue = wide_frame_queue
        self.graph_data_queue = graph_data_queue
        self.graph_diff_queue = graph_diff_queue

        self.index_picture = 0

        # init functions
        self.init_menu(window_title)
        self.init_title()
        self.init_bottom_text()
        self.init_data_holders()
        self.init_graph_area()
        self.init_cameras()
        self.init_buttons()

        self.closed = False

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.frame_delay = 15
        self.graph_delay = 250

        self.ani1 = animation.FuncAnimation(self.diff_data.fig, self.animate1, interval=self.graph_delay)
        self.ani2 = animation.FuncAnimation(self.abs_loc_data.fig, self.animate2, interval=self.graph_delay)
        self.update_all()

    def animate1(self, i):
        self.diff_data.plot_update(names=["Target offset"])

    def animate2(self, i):
        self.abs_loc_data.plot_update(names=["Target position", "Gimbal position"])

    def init_menu(self, window_title):
        self.window = Tk()
        self.window.title(window_title)
        self.window.geometry("1920x1080")
        # window.iconbitmap("drone_logo_yPm_icon.ico")
        self.window.config(background='#2E313B')

    def init_title(self):
        self.frame_top = Frame(self.window,
                               bg=self.main_bg,
                               bd=0,
                               relief=SUNKEN)

        self.title_font = font.Font(family="Calibri", size=40, weight="bold")

        self.label_title = Label(self.frame_top,
                                 text="Drone Surveillance System",
                                 font=self.title_font,
                                 bg=self.main_bg,
                                 fg='white')
        self.frame_top.pack()
        self.frame_top.place(relx=0, rely=0, relheight=0.05, relwidth=1)
        self.label_title.pack(fill=BOTH, expand=True)
        self.label_title.bind("<Configure>", self.resize_title)

    def resize_title(self, event):
        self.title_font['size'] = event.height // 2

    def init_bottom_text(self):
        self.frame_bottom = Frame(self.window, bg=self.main_bg, bd=2, relief=SUNKEN)
        self.label_bottom1 = Label(self.frame_bottom,
                                   text="Drone Detection Project - Amir Sarig & Michael Aboulhair",
                                   font=("Calibri", 15),
                                   bg=self.main_bg,
                                   fg='gray')
        self.label_bottom11 = Label(self.frame_bottom,
                                    text="Supervised by Johanan Erez, Eli Appleboim, Israel Berger and Yossi Bar Erez",
                                    font=("Calibri", 15),
                                    bg=self.main_bg,
                                    fg='gray')
        self.label_bottom2 = Label(self.frame_bottom,
                                   text="Technion - Israel Institute of Technology, Department of Electrical Engineering",
                                   font=("Calibri", 15),
                                   bg=self.main_bg,
                                   fg='gray')
        self.label_bottom3 = Label(self.frame_bottom,
                                   text="Vision and Image Sciences Laboratory (VISL)",
                                   font=("Calibri", 15),
                                   bg=self.main_bg,
                                   fg='gray')
        self.label_bottom4 = Label(self.frame_bottom, text="2018/2019", font=("Calibri", 15), bg=self.main_bg,
                              fg='gray')
        self.image_VISL = PhotoImage(file="OurFunctions/Gui_images/logo_visl.png")
        self.label_logo_VISL = Label(self.frame_bottom, image=self.image_VISL)
        self.label_logo_VISL.pack(side=RIGHT, padx=10)
        self.image_technion = PhotoImage(file="OurFunctions/Gui_images/logo_technion.png")
        self.label_logo_technion = Label(self.frame_bottom, image=self.image_technion)

        self.frame_bottom.pack()
        self.frame_bottom.place(relx=0, rely=0.85, relheight=0.15, relwidth=1)


        self.label_logo_technion.pack(side=LEFT, padx=10)
        self.label_bottom1.pack()
        self.label_bottom11.pack()
        self.label_bottom2.pack()
        self.label_bottom3.pack()
        self.label_bottom4.pack()

    def init_data_holders(self):
        self.abs_loc_data = DataHolder()
        self.abs_loc_data.add_param("Target position", color='b')
        self.abs_loc_data.add_param("Gimbal position", color='r')
        self.abs_loc_data.add_param("Target speed", color='g')

        self.abs_loc_data.plot_init("time[s]", "position[degrees]", "Target vs Gimbal position",
                                    names=["Target position", "Gimbal position"])

        self.diff_data = DataHolder()
        self.diff_data.add_param("Target offset", color='b')
        #self.diff_data.add_param("estimated diff", color='r')

        self.diff_data.plot_init("time[s]", "offset[angles]", "Target offset from camera center",
                                 names=["Target offset"])

    def init_cameras(self):
        self.camera_title_font = font.Font(family="Calibri", size=20, weight="bold")
        self.init_zoom_area()
        self.init_wide_area()

    def init_zoom_area(self):
        self.frame_right_zoom = Frame(self.window, bg='#2E313B', bd=2, relief=GROOVE)
        self.label_right_zoom = Label(self.frame_right_zoom, text="Telephoto Camera", font=self.camera_title_font,
                                      bg='#2E313B', fg='white')
        self.main_right_zoom = Label(self.frame_right_zoom)

        self.frame_right_zoom.pack()
        self.frame_right_zoom.place(relx=0.55, rely=0.05, relheight=0.5, relwidth=0.45)
        self.frame_right_zoom.bind('<Escape>', lambda e: self.frame_right_zoom.quit())

        self.label_right_zoom.pack()
        self.label_right_zoom.place(relx=0, rely=0, relheight=0.1, relwidth=1)
        self.label_right_zoom.bind("<Configure>", self.resize_camera_title)

        self.main_right_zoom.pack()
        self.main_right_zoom.place(anchor="n", relx=0.5, rely=0.1, relheight=0.9, relwidth=1)

    def init_wide_area(self):
        self.frame_left_wide = Frame(self.window, bg='#2E313B', bd=2, relief=GROOVE)
        self.label_left_wide = Label(self.frame_left_wide, text="Wide Camera", font=self.camera_title_font,
                                     bg='#2E313B', fg='white')
        self.main_left_wide = Label(self.frame_left_wide)

        self.frame_left_wide.pack()
        self.frame_left_wide.place(relx=0, rely=0.05, relheight=0.5, relwidth=0.45)
        self.frame_left_wide.bind('<Escape>', lambda e: self.frame_left_wide.quit())

        self.label_left_wide.pack()
        self.label_left_wide.place(relx=0, rely=0, relheight=0.1, relwidth=1)
        self.label_left_wide.bind("<Configure>", self.resize_camera_title)

        self.main_left_wide.pack()
        self.main_left_wide.place(anchor="n", relx=0.5, rely=0.1, relheight=0.9, relwidth=1)

    def resize_camera_title(self, event):
        self.camera_title_font["size"] = event.height // 2

    def init_graph_area(self):
        self.frame_graphs = Frame(self.window, bg='#2E313B', bd=2, relief=GROOVE)
        self.frame_graphs.bind('<Escape>', lambda e: self.frame_graphs.quit())

        self.frame_target_graph = Frame(self.frame_graphs, bd=2, relief=GROOVE)
        self.target_graph = FigureCanvasTkAgg(self.abs_loc_data.fig, self.frame_target_graph)

        self.frame_diff_graph = Frame(self.frame_graphs, bd=2, relief=GROOVE)
        self.diff_graph = FigureCanvasTkAgg(self.diff_data.fig, self.frame_diff_graph)
        self.diff_graph.get_tk_widget().pack()

        self.frame_graphs.pack()
        self.frame_graphs.place(relx=0, rely=0.55, relheight=0.3, relwidth=1)

        self.frame_target_graph.pack()
        self.frame_diff_graph.pack()
        self.frame_target_graph.place(relx=0, rely=0, relheight=1, relwidth=0.5)
        self.frame_diff_graph.place(relx=0.5, rely=0, relheight=1, relwidth=0.5)

        self.target_graph.get_tk_widget().pack(expand=True, fill=BOTH)
        self.diff_graph.get_tk_widget().pack(expand=True, fill=BOTH)

    def resize_target_graph(self, event):
        pass

    def init_buttons(self):
        # button quit
        self.frame_button = Frame(self.window,
                                  bg=self.main_bg,
                                  bd=0,
                                  relief=GROOVE)
        self.quit_button = Button(self.frame_button,
                                  bg=self.main_bg,
                                  highlightthickness=0,
                                  bd=0,
                                  relief=GROOVE,
                                  command=self.quit)
        self.close_icon = PhotoImage(file="OurFunctions/Gui_images/close_icon_70x70.png")
        self.quit_button.config(image=self.close_icon,
                                bg=self.main_bg,
                                highlightthickness=0,
                                bd=0,
                                relief=GROOVE)

        # button save picture
        self.take_picture_button = Button(self.frame_button,
                                          bg=self.main_bg,
                                          highlightthickness=0,
                                          bd=0,
                                          relief=GROOVE,
                                          command=self.take_picture)
        self.camera_icon = PhotoImage(file="OurFunctions/Gui_images/camera_icon_70x70.png")
        self.take_picture_button.config(image=self.camera_icon,
                                        bg=self.main_bg,
                                        highlightthickness=0,
                                        bd=0,
                                        relief=GROOVE)

        self.image_system = PhotoImage(file="OurFunctions/Gui_images/system_150x208.png")
        self.label_system = Label(self.frame_button, image=self.image_system, bg=self.main_bg)

        self.frame_button.pack()
        self.frame_button.place(relx=0.45, rely=0.05, relheight=0.5, relwidth=0.1)
        self.quit_button.pack(pady=10)
        self.take_picture_button.pack(pady=20)
        self.label_system.pack(side=BOTTOM, pady=20)

    def quit(self):
        self.closed = True
        self.ani1.event_source.stop()
        self.ani2.event_source.stop()

    def take_picture(self):
        self.picName = "OurFunctions/pictures/pic" + str(self.index_picture) + ".jpg"
        self.index_picture += 1
        cv2.imwrite(self.picName, self.frame_left_wide)

    def run(self):
        self.window.mainloop()

    def update_zoom_frame(self):
        if not self.zoom_frame_queue.empty():
            # prepare zoom frame
            next_frame = self.zoom_frame_queue.get()
            frame_height, frame_width, _ = next_frame.shape
            widg_height = self.main_right_zoom.winfo_height()
            widg_width = self.main_right_zoom.winfo_width()

            resize_height = widg_height / frame_height
            resize_width = widg_width / frame_width

            resize_factor = min(resize_height, resize_width)

            frame_zoom = cv2.cvtColor(next_frame, cv2.COLOR_BGR2RGBA)
            frame_zoom_resized = cv2.resize(frame_zoom, (0, 0), fx=resize_factor, fy=resize_factor)
            frame_zoom_PIL = PIL.Image.fromarray(frame_zoom_resized)
            frame_zoom_TK = ImageTk.PhotoImage(image=frame_zoom_PIL)

            # update zoom frame
            self.main_right_zoom.imgtkZoom = frame_zoom_TK
            self.main_right_zoom.configure(image=frame_zoom_TK)

        # update window
        self.window.update_idletasks()
        self.window.update()

    def update_wide_frame(self):
        # prepare wide frame
        frame_wide = cv2.cvtColor(self.wide_frame_queue.get(), cv2.COLOR_BGR2RGBA)
        frame_wide_resized = cv2.resize(frame_wide, (0, 0), fx=0.7, fy=0.7)
        frame_wide_PIL = PIL.Image.fromarray(frame_wide_resized)
        frame_wide_TK = ImageTk.PhotoImage(image=frame_wide_PIL)


        # update wideframe
        self.main_left_wide.imgtkWide = frame_wide_TK
        self.main_left_wide.configure(image=frame_wide_TK)
        self.main_left_wide._image_cache = frame_wide_TK

        # update window
        self.window.update_idletasks()
        self.window.update()

    def update_graph_frame(self):
        # prepare graph:
        while not self.graph_data_queue.empty():
            graph_data = self.graph_data_queue.get()
            self.abs_loc_data.log(graph_data)

        while not self.graph_diff_queue.empty():
            graph_diff = self.graph_diff_queue.get()
            self.diff_data.log(graph_diff)

    def update_all(self):

        if not self.closed:
            self.update_zoom_frame()
            # self.update_wide_frame() TODO: uncomment when ready
            self.update_graph_frame()
            self.window.after(self.frame_delay, self.update_all)
        else:
            self.export_graphs("ramp")
            self.window.destroy()

    def export_graphs(self, file_base_name):
        self.abs_loc_data.export_all(file_base_name + "_location_info.csv")
        self.diff_data.export_all(file_base_name + "_diff_info.csv")




