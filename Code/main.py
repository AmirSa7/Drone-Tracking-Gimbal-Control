import threading, queue
import multiprocessing
from yolov5.detect import detect_wrap
from OurFunctions.gui import Gui
import csv


if __name__ == "__main__":
    zoom_frame_queue = multiprocessing.Queue()
    wide_frame_queue = multiprocessing.Queue()
    graph_data_queue = multiprocessing.Queue()
    graph_diff_queue = multiprocessing.Queue()
    quit_msg_queue = multiprocessing.Queue()

    # creating thread for GUI
    thread_detect_1 = multiprocessing.Process(target=detect_wrap, args=(zoom_frame_queue, graph_data_queue, graph_diff_queue, quit_msg_queue))
    #thread_detect_2 = threading.Thread(target=detect_wrap, args=(wide_frame_queue,quit_msg_queue), daemon=True)

    # starting thread 1
    thread_detect_1.start()

    # create intance of the GUI
    gui = Gui(zoom_frame_queue, wide_frame_queue, graph_data_queue, graph_diff_queue, "Drone Surveillance System")

    gui.run()

    quit_msg_queue.put(True)
    thread_detect_1.join()
    # both threads completely executed

    with open('ramp_diff_info.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        diffs = list(reader)[1]

    diffs = list(eval(diffs[0]))
    
    mmse = sum([diff**2 for diff in diffs]) / len(diffs)

    print("MMSE = {}".format(mmse))	
