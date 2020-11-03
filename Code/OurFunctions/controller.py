import serial
import struct
import numpy as np
import time
from OurFunctions.helpers import *


class Integrator:
    def __init__(self, start_value=0, max_delta=0.1):
        self.reset_value = start_value
        self.sum = start_value
        self.prev_time = time.time()
        self.max_delta=max_delta

    def f(self, value):
        now = time.time()
        delta = min(now - self.prev_time, self.max_delta)
        self.sum += value * delta
        self.prev_time = now
        return self.sum

    def reset(self):
        self.sum = self.reset_value


class Controller:

    def __init__(self, sys_type=1, gains=None, speed_gain=0):
        # System Constants
        self.speed_gain = speed_gain

        self.sys_type = sys_type
        if gains is None:
            self.gains = [1]
        else:
            self.gains = gains

        self.integrators = [Integrator() for _ in range(sys_type)]

    def output(self, relative_target_position_theta, target_speed=0):

        val = 0

        for i in reversed(range(self.sys_type)):
            val += relative_target_position_theta * self.gains[i]
            if i > 0:
                val = self.integrators[i].f(val)

        val += self.speed_gain * target_speed

        return val

    def reset(self):
        [integrator.reset() for integrator in self.integrators]

