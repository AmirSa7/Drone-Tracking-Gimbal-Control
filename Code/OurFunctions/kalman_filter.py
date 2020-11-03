import numpy as np
from scipy.linalg import solve_discrete_are as dare


class KalmanFilter:
    def __init__(self, A, C, x_init, W, V, P_init=None ,stationary=False):

        self.A = A
        self.C = C

        self.x_est = x_init
        self.x_pred = x_init

        self.W = W  # System noise covariance
        self.V = V  # Measurement noise covariance

        self.stationary = stationary

        if not stationary:
            if not P_init:
                P_init = np.eye(np.size(A, 1))
            self.P_est = P_init
            self.P_pred = P_init

        if stationary:
            P = dare(A.T, C.T, W, V)
            self.K = P @ C.T * (1/(C @ P @ C.T + V))

    def predict(self, set_estimation=False):
        self.x_pred = self.A @ self.x_est
        if set_estimation:
            self.x_est = self.x_pred
        if not self.stationary:
            self.P_pred = self.A @ self.P_est @ self.A.T + self.W

    def estimate(self, measurement):
        if self.stationary:
            self.x_est = self.x_pred + self.K * (measurement - self.C @ self.x_pred)
        else:
            K = self.P_pred @ self.C.T * (1 / (self.C @ self.P_pred @ self.C.T + self.V))
            self.x_est = self.x_pred + K * (measurement - self.C @ self.x_pred)
            self.P_est = (np.eye(3) - K @ self.C) @ self.P_pred

    def input(self, measurement):
        self.predict()
        self.estimate(measurement)

    def get_forward_prediction(self, num_steps):
        Ap = np.linalg.matrix_power(self.A, num_steps)
        pred = Ap @ self.x_pred
        return tuple(*pred.T)

    def get_state_est(self):
        return tuple(*self.x_est.T)

    def get_state_pred(self):
        return tuple(*self.x_pred.T)

    def setA(self, A):
        self.A = A

    def setC(self, C):
        self.C = C

    def set_init(self, x_init):
        self.x_est = x_init
        self.x_pred = x_init