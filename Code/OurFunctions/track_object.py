import numpy as np
import time

from OurFunctions.gimbal import Gimbal, PsoudoGimbal
from OurFunctions.kalman_filter import KalmanFilter
from OurFunctions.controller import Controller
from OurFunctions.helpers import get_xmid_ymid, get_deg_pix_conv, gentle_put


class Tracker:
    def __init__(self,
                 arduino_device_path,
                 graph_data_queue,
                 graph_diff_queue,
                 img_width=1280,
                 img_height=720,
                 working_distance=5,
                 blind_steps=10,
                 camera_delay=0.2,
                 delay_gimbal=True,
                 stationary=False,
                 use_kalman=True):

        self.img_width = img_width
        self.img_height = img_height
        self.graph_data_queue = graph_data_queue
        self.graph_diff_queue = graph_diff_queue
        if arduino_device_path:
            self.gimbal = Gimbal(arduino_device_path, delay=camera_delay)

        else:
            self.gimbal = PsoudoGimbal()

        self.use_kalman = use_kalman

        if use_kalman:
            x_init = np.array([[0],
                               [0],
                               [0]])

            # define noise variables
            W_x = np.array([[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 10]])  # the covariance of the noise of the state parameters in the X axis

            # define noise variables
            W_y = np.array([[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 5]])  # the covariance of the noise of the state parameters in the Y axis

            V = 0.05  # the covariance of the noise of the measurement

            delta_0 = 1 / 30

            # define matrices:
            A = np.array([[1, delta_0, 0.5 * delta_0 * delta_0],
                          [0, 1, delta_0],
                          [0, 0, 1]])

            C = np.array([[1, 0, 0]])  # in our case y_k = x_k

            self.stationary = stationary
            self.kalman_x = KalmanFilter(A, C, x_init, W_x, V, stationary=stationary)
            self.kalman_y = KalmanFilter(A, C, x_init, W_y, V, stationary=stationary)

        self.controller_x = Controller(sys_type=2, gains=[6, 6, 0], speed_gain=0.1)
        self.controller_y = Controller(sys_type=2, gains=[6, 6, 0], speed_gain=0.1)

        self.prev_time = time.time()
        self.blind_steps = blind_steps
        self.blind_steps_taken = 0

        self.untrack = True

        self.prev_time = time.time()

        self.alpha, self.beta = get_deg_pix_conv(working_distance)

        self.delta_avg = 0.05  # Starting value is measured average in experiments
        self.samples = 0
        self.camera_delay = camera_delay
        self.delay_gimbal = delay_gimbal

    def update_delta(self, delta):
        if self.use_kalman:
            A = np.array([[1, delta, 0.5 * delta * delta],
                          [0, 1, delta],
                          [0, 0, 1]])
            self.kalman_x.setA(A)
            self.kalman_y.setA(A)

        self.delta_avg *= self.samples
        self.delta_avg += delta
        self.samples += 1
        self.delta_avg /= self.samples

    def get_target_relative_position(self, det, cls=None):

        # Get position of target on screen in pixels
        x_cord, y_cord = get_xmid_ymid(det)

        # Get distance in pixels from target position to center
        # Our axes are defined so that in the X axis -> right is positive, in the Y axis -> up is positive
        x_diff = x_cord - self.img_width / 2
        y_diff = self.img_height / 2 - y_cord

        # Convert pixel difference to degrees
        # We assume that the distance stays roughly the same so that the conversion is valid

        x_deg_diff = x_diff * self.alpha
        y_deg_diff = y_diff * self.alpha

        return x_deg_diff, y_deg_diff

    def get_gimbal_pos(self):
        if self.delay_gimbal:
            return self.gimbal.get_delayed_position()
        else:
            return self.gimbal.get_position()

    def get_target_global_position(self, det, cls=None):

        x_deg_diff, y_deg_diff = self.get_target_relative_position(det, cls)
        gimbal_x_pos, gimbal_y_pos = self.get_gimbal_pos()
        return gimbal_x_pos + x_deg_diff, gimbal_y_pos + y_deg_diff

    def track_kalman(self, det, cls=None, forward_prediction=False):

        # Measure position
        x_pos, y_pos = self.get_target_global_position(det, cls)
        gimbal_x_now, gimbal_y_now = self.gimbal.get_position()

        now = time.time()

        if self.untrack:
            self.kalman_x.set_init(np.array([[x_pos],
                                             [0],
                                             [0]]))
            self.kalman_y.set_init(np.array([[y_pos],
                                             [0],
                                             [0]]))
            self.untrack = False
        else:
            delta = now - self.prev_time
            self.update_delta(delta)

            # Apply to kalman filters
            self.kalman_x.input(x_pos)
            self.kalman_y.input(y_pos)

        pred_steps = int(self.camera_delay / self.delta_avg)
        x_pos_pred, x_velocity_pred, x_acc_pred = self.kalman_x.get_forward_prediction(pred_steps)
        y_pos_pred, y_velocity_pred, y_acc_pred = self.kalman_y.get_forward_prediction(pred_steps)

        # Possible delayed variables
        x_pos, x_velocity, x_acc = self.kalman_x.get_state_est()
        y_pos, y_velocity, y_acc = self.kalman_y.get_state_est()

        self.prev_time = now

        if forward_prediction:
            v_x = self.controller_x.output(x_pos_pred - gimbal_x_now, target_speed=x_velocity)
            v_y = self.controller_y.output(y_pos_pred - gimbal_y_now, target_speed=y_velocity)
            self.graph_data_queue.put([now, x_pos_pred, gimbal_x_now, x_velocity_pred])

        else:
            v_x = self.controller_x.output(x_pos - gimbal_x_now, target_speed=x_velocity)
            v_y = self.controller_y.output(y_pos - gimbal_y_now, target_speed=y_velocity)
            self.graph_data_queue.put([now, x_pos, gimbal_x_now, x_velocity])

        self.graph_diff_queue.put([now, self.get_target_relative_position(det, cls)[0]])

        self.gimbal.set_speeds_degs(v_x, v_y)

        self.blind_steps_taken = 0

    def track_direct(self, det, cls=None):
        x_deg_diff, y_deg_diff = self.get_target_relative_position(det, cls)

        v_x = self.controller_x.output(x_deg_diff)
        v_y = self.controller_y.output(y_deg_diff)

        self.gimbal.set_speeds_degs(v_x, v_y)

    def track(self, det, cls=None, forward_prediction=False):
        if self.use_kalman:
            self.track_kalman(det, cls, forward_prediction)
        else:
            self.track_direct(det, cls)

    def blind_track(self, forward_prediction=0):
        if not self.use_kalman:
            self.gimbal.stop()
            return

        gimbal_x_pos, gimbal_y_pos = self.get_gimbal_pos()
        gimbal_x_now, gimbal_y_now = self.gimbal.get_position()

        now = time.time()

        if self.untrack:
            self.gimbal.stop()
            self.controller_x.reset()
            self.controller_y.reset()
            self.prev_time = now
        else:

            delta = now - self.prev_time
            self.update_delta(delta)
            self.prev_time = now

            # Apply kalman filters with prediction only
            self.kalman_x.predict(set_estimation=True)
            self.kalman_y.predict(set_estimation=True)

            pred_steps = int(self.camera_delay / self.delta_avg)
            x_pos_pred, x_velocity_pred, x_acc_pred = self.kalman_x.get_forward_prediction(pred_steps)
            y_pos_pred, y_velocity_pred, y_acc_pred = self.kalman_y.get_forward_prediction(pred_steps)

            # Possible delayed variables
            x_pos, x_velocity, x_acc = self.kalman_x.get_state_est()
            y_pos, y_velocity, y_acc = self.kalman_y.get_state_est()

            self.prev_time = now

            if forward_prediction:
                v_x = self.controller_x.output(x_pos_pred - gimbal_x_now, target_speed=x_velocity)
                v_y = self.controller_y.output(y_pos_pred - gimbal_y_now, target_speed=y_velocity)
                gentle_put(self.graph_data_queue, [now, x_pos_pred, gimbal_x_now, x_velocity_pred])

            else:
                v_x = self.controller_x.output(x_pos - gimbal_x_now, target_speed=x_velocity)
                v_y = self.controller_y.output(y_pos - gimbal_y_now, target_speed=y_velocity)
                gentle_put(self.graph_data_queue, [now, x_pos, gimbal_x_now, x_velocity])

            self.gimbal.set_speeds_degs(v_x, v_y)

            self.blind_steps_taken += 1

        if self.blind_steps == self.blind_steps_taken:
            self.untrack = True

    # def export_graph(self, name):
    #     self.graph.export_all(name + "_location_info.csv")
    #     self.diff.export_all(name + "_diff_info.csv")
    #
    # def send_data(self, data, queue):
    #     self.queue.put(data)
