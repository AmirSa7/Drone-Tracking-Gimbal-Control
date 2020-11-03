from enum import Enum
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time
import PIL
import csv
from matplotlib.figure import Figure

def gentle_put(queue, element):
    # prevents overload of the queue
    if queue.empty():
        queue.put(element)
    else:
        return

def get_xmid_ymid(det):
    (xtl, ytl), (xbr, ybr) = get_tl_br(det)
    x_mid = int((xtl+xbr)/2)
    y_mid = int((ytl+ybr)/2)
    return x_mid, y_mid


def get_tl_br(det):
    x_top_left = int(det[0][0])
    y_top_left = int(det[0][1])
    x_btm_right = int(det[0][2])
    y_btm_right = int(det[0][3])
    return (x_top_left, y_top_left), (x_btm_right, y_btm_right)

def get_deg_pix_conv(working_distance):
    alpha_0 = 0.0045
    beta_0 = 2510
    default_focal_length = 5

    alpha = alpha_0 * 5 / working_distance
    beta = beta_0 * 5 / working_distance

    return alpha, beta


class QueueArray:
    def __init__(self, size):
        self.arr = list()
        self.size = size
        self.curr_size = 0

    def insert(self, value):

        self.arr.insert(self.curr_size, value)
        if self.curr_size == self.size:
            self.arr.pop(0)
        else:
            self.curr_size += 1

class PlotInfo:
    def __init__(self, size, name, marker=".", color="b"):
        self.data = QueueArray(size)
        self.name = name
        self.marker = marker
        self.color = color


# A class for keeping all logged data
class DataHolder:
    # init method or constructor
    def __init__(self, size=200):
        self.size = size
        self.params = list()
        self.time = QueueArray(size)
        self.start_time = time.time()

        self.fig = Figure(tight_layout=True)
        self.sub = self.fig.add_subplot(1, 1, 1)
        self.lines = dict()

    # Methodes
    def add_param(self, name, marker=".", color='b'):
        self.params.append(PlotInfo(self.size, name, marker, color))

    def log(self, values):
        curr_time = values[0]
        values.pop(0)
        if len(values) != len(self.params):
            print("Error: number of values passed to log doesn't match the number of parameters defined")
            return
        self.time.insert(curr_time - self.start_time)
        for i, param in enumerate(self.params):
            param.data.insert(values[i])

    def plot_init(self, x_label, y_label, title, names):
        for param in self.params:
            if param.name in names:
                self.lines[param.name], = self.sub.plot(self.time.arr,
                                                         param.data.arr,
                                                         marker=param.marker,
                                                         color=param.color,
                                                         label=param.name,
                                                         linestyle='None')

        self.sub.set_xlabel(x_label)
        self.sub.set_ylabel(y_label)
        self.sub.set_title(title)
        self.sub.legend(loc=2)
        # sub.legend()
        # plt.legend()
        # plt.show()
        # fig.canvas.draw()
        #image = PIL.Image.frombytes('RGB', self.sub.get_width_height(), sub.tostring_rgb()).copy()
        #sub.close(fig)
        #return image

    def plot_update(self, names):
        for param in self.params:
            if param.name in names:
                self.lines[param.name].set_data(self.time.arr, param.data.arr)
        self.sub.relim()
        self.sub.autoscale_view()

    def plot_all_init(self, x_label, y_label, title):
        self.plot_init(x_label, y_label, title, [param.name for param in self.params])

    def plot_all_update(self, names):
        self.plot_update([param.name for param in self.params])

    # def draw_plot(self):
    #     plt.draw()

    def export(self, file, names):
        with open(file, 'w', newline='') as my_data:
            wr = csv.writer(my_data)
            wr.writerow(self.time.arr)
            for param in self.params:
                if param.name in names:
                    wr.writerow(param.data.arr)

    def export_all(self, file):
        self.export(file, [param.name for param in self.params])



