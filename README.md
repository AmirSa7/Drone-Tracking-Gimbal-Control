## Description
This project combines stepper motors, telephoto camera, Arduino nano and A4988 driver into a system capable of tracking a drone in real time.

Our system consists of a camera mounted on an open-loop stepper pan & tilt unit. The camera captures a frame and feeds it to a DNN, which gives us the pixel coordinates of a drone within it. These coordinates are the input to our system, and our goal is to control the motors so that the target is centered in the camera.
Implementing a good target following system may be useful for various applications such as: 
1.	recording fast moving object like birds, bats or insects.
2.	Shooting down military invasive targets
3.	Maintaining beam-based communication with a moving system.
Doing it well enough using relatively cheap, off-the-shelf parts is challenging. In this project we are using a drone as the moving target.
In our work we have simulated this discrete, opened loop system, paying attention to the added detection noise as well as hardware and software delays.
To achieve good performance, we have used Kalman Filter, PID Controller and a Predictor.  We have simulated (Simulink) various configurations of these elements and fined tuned the constants. Then we implemented a PID controller in code (Python, Jetson) and 2 axes simultaneous speed controller to drive the motors (C++, Arduino). Finally, we have performed real-life experiments and measurements to confirm the theory and the simulation.


The DNN being used in this project is YOLOv5 from: https://github.com/ultralytics/yolov5 were detect.py was modified in order to fit our needs.

<img src="https://github.com/AmirSa7/Drone-Tracking-Gimbal-Control/blob/main/Report/Report%20images/the_system_ver02.png" width="1000"></a>
