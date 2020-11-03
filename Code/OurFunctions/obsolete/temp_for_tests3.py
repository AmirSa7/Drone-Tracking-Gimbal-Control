import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from random import randint
import time



import cv2
import matplotlib.pyplot as plt

def grab_frame(cap):
    ret,frame = cap.read()
    return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

# This function is called periodically from FuncAnimation
def animate(xs, ys):

    # Read temperature (Celsius) from TMP102
    temp_c = round(ys[-1] + randint(-2, 2), 2)

    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
    ys.append(temp_c)

    # Limit x and y lists to 20 items
    xs = xs[-20:]
    ys = ys[-20:]

    # Draw x and y lists
    ax2.clear()
    ax2.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('TMP102 Temperature over Time')
    plt.ylabel('Temperature (deg C)')

#Initiate the two cameras
cap1 = cv2.VideoCapture(0)

#create two subplots
ax1 = plt.subplot(1,2,1)
ax2 = plt.subplot(1,2,2)
xs = [0]
ys = [0]

#create two image plots
im1 = ax1.imshow(grab_frame(cap1))
im2, = ax2.plot([], [])

plt.ion()

while True:
    start = time.time()

    im1.set_data(grab_frame(cap1))
    animate(xs, ys)
    im2.set_xdata(xs)
    im2.set_ydata(ys)

    end = time.time()
    print(end - start)
    plt.pause(0.01)

plt.ioff()  # due to infinite loop, this gets never called.
plt.show()

