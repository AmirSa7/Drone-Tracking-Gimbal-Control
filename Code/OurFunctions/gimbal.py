import time
import serial
from enum import Enum
from struct import pack
import numpy as np


class GimbalCommands(Enum):
    RESET = 101
    TEST_HORZ_SPEED = 102
    TEST_VERT_SPEED = 103
    SET_HORZ_SPEED_MOD = 104
    SET_VERT_SPEED_MOD = 105
    SET_PULSE = 106


def acc_sleep(seconds):
    now = time.time()
    while time.time() - now < seconds:
        pass


# Cyclic list to help store past positions
class CyclicList:
    def __init__(self, size):
        self.list = np.zeros((1, size))
        self.size = size
        self.iterator_first = 0
        if size > 1:
            self.iterator_last = 1
        else:
            self.iterator_last = 0

    def insert(self, value):
        self.iterator_first = (self.iterator_first + 1) % self.size
        self.iterator_last = (self.iterator_last + 1) % self.size
        self.list[0][self.iterator_first] = value


    def last(self):
        return self.list[0][self.iterator_last]


class Gimbal:
    def __init__(self,
                 arduino_device_path,
                 pulse_len=10,
                 horz_modifier=28,
                 vert_modifier=32,
                 step_size=0.025,
                 delay=0.1,
                 resolution=0.0001,
                 reset_position=False,
                 range_x=360,
                 range_y=111,
                 range_y_top=31):
        # Start with gimbal position 0
        self.pos_x = 0
        self.pos_y = 0

        self.resolution = resolution

        self.history_size = int(delay/resolution)

        # Store past positions of the gimbal
        self.pos_x_history = CyclicList(self.history_size)
        self.pos_y_history = CyclicList(self.history_size)

        # Start with gimbal speed 0
        self.speed_x = 0
        self.speed_y = 0

        self.prev_time = time.time()
        self.ard = serial.Serial(arduino_device_path, timeout=1)

        self.pulse_len = pulse_len
        self.horz_modifier = horz_modifier
        self.vert_modifier = vert_modifier
        self.step_size = step_size

        self.range_x = range_x
        self.range_y = range_y
        self.range_y_top = range_y_top
        self.reset_position = reset_position

        # Reset first to ensure Gimbal is stopped and all its parameters are set
        self.reset()
        self.stopped = True

    # Write byte to arduino. If byte param will be cast to np.uint8
    def write(self, byte):
        self.ard.write(pack('B', np.uint8(int(byte))))

    def reset(self):
        self.write(GimbalCommands.RESET.value)
        # reset might change some params from the initial params, so we change them back
        self.set_pulse_len(self.pulse_len)
        self.set_horz_modifier(self.horz_modifier)
        self.set_vert_modifier(self.vert_modifier)

        if self.reset_position:
            self.go_to_0()

        self.pos_x = 0
        self.pos_y = 0
        self.speed_x = 0
        self.speed_y = 0

    # Set speed in % of max speed
    def set_speeds(self, horz, vert):

        if horz < -100 or horz > 100 or vert < -100 or vert > 100:
            print("Gimbal speed must be a value between -100 and 100")

        # Set new speed in arduino
        self.write(horz)
        self.write(vert)

        # Update position before we update the speed, because update is according to previous speed
        self.update_position()

        # Update the speed second
        self.speed_x = self.calc_horz_speed(np.int8(horz))
        self.speed_y = self.calc_horz_speed(np.int8(vert))

        if horz != 0 or vert != 0:
            self.stopped = False

    # Set speed in units of degs/sec
    def set_speeds_degs(self, horz, vert):

        max_horz = self.calc_max_horz_speed()
        max_vert = self.calc_max_vert_speed()

        # Limit speed to gimbal maximum
        horz = np.clip(horz, -max_horz, max_horz)
        vert = np.clip(vert, -max_vert, max_vert)

        # Get speed in % from max
        horz_perc = horz * 100 / max_horz
        vert_perc = vert * 100 / max_vert

        # Set speeds in percent
        self.set_speeds(horz_perc, vert_perc)

    def stop(self):
        # To avoid calling set_speeds multiple times, check if the stopped variable is False
        if not self.stopped:
            self.set_speeds(0, 0)
        self.stopped = True

    def get_position(self):
        self.update_position()
        return self.pos_x, self.pos_y

    def get_delayed_position(self):
        self.update_position()
        return self.pos_x_history.last(), self.pos_y_history.last()

    def update_position(self):
        curr_time = time.time()
        time_delta = curr_time - self.prev_time
        # Update the positional history first
        for i in range(int(time_delta / self.resolution)):
            self.pos_x_history.insert(self.pos_x + self.speed_x * i * self.resolution)
            self.pos_y_history.insert(self.pos_y + self.speed_y * i * self.resolution)

        # Then update the real time position
        self.pos_x = self.pos_x + self.speed_x * time_delta
        self.pos_y = self.pos_y + self.speed_y * time_delta

        self.prev_time = curr_time

    # Sets the pulse len in the arduino to 10 * pulse_len
    def set_pulse_len(self, pulse_len):
        self.write(GimbalCommands.SET_PULSE.value)
        self.write(pulse_len)

    # Sets the horizontal speed modifier in the arduino to 1000 * mod
    def set_horz_modifier(self, mod):
        self.write(GimbalCommands.SET_HORZ_SPEED_MOD.value)
        self.write(mod)

    # Sets the vertical speed modifier in the arduino to 1000 * mod
    def set_vert_modifier(self, mod):
        self.write(GimbalCommands.SET_VERT_SPEED_MOD.value)
        self.write(mod)

    # calculate maximum speed in degrees per second, according to step size and speed modifier
    def calc_max_speed(self, speed_mod):
        step_time_us = speed_mod * 10
        step_time_s = step_time_us / 1000000
        return self.step_size / step_time_s

    def calc_max_horz_speed(self):
        return self.calc_max_speed(self.horz_modifier)

    def calc_max_vert_speed(self):
        return self.calc_max_speed(self.vert_modifier)

    #calculate physical speed according to input that is between -100 and 100
    def calc_horz_speed(self, input_speed):
        return input_speed * self.calc_max_horz_speed() / 100

    def calc_vert_speed(self, input_speed):
        return input_speed * self.calc_max_vert_speed() / 100

    # Move gimbal 180 degrees in each horizontal direction, starting clockwise
    def test_horz_speed(self):
        self.write(GimbalCommands.TEST_HORZ_SPEED.value)

    # Move gimbal 90 degrees in each vertical direction, starting upwards
    def test_vert_speed(self):
        self.write(GimbalCommands.TEST_VERT_SPEED.value)

    def close(self):
        if self.ard.is_open:
            self.stop()
            self.ard.close()

    # Move in specified speed for specified time in each axis
    def move_time(self, x_time, y_time, x_speed, y_speed):
        first_wait = min(x_time, y_time)
        second_wait = max(x_time, y_time) - first_wait

        if first_wait != 0:
            self.set_speeds_degs(x_speed, y_speed)
            acc_sleep(first_wait)
        if x_time > y_time:
            self.set_speeds_degs(x_speed, 0)
        else:
            self.set_speeds_degs(0, y_speed)
        acc_sleep(second_wait)
        self.stop()

    # Go to starting position of gimbal
    def go_to_start(self):
        x_pos, y_pos = self.get_position()
        x_speed = self.calc_max_horz_speed() * -np.sign(x_pos)
        y_speed = self.calc_max_vert_speed() * -np.sign(y_pos)

        x_time = x_pos/-x_speed
        y_time = y_pos/-y_speed

        self.move_time(x_time, y_time, x_speed, y_speed)

    # Go to zero position, according to specified ranges
    def go_to_0(self):
        x_speed = self.calc_max_horz_speed()
        y_speed = self.calc_max_vert_speed()

        print(x_speed)
        print(y_speed)

        x_time = self.range_x / x_speed
        y_time = self.range_y / y_speed

        print(x_time)
        print(y_time)

        # Move to the edge of the gimbal possible position
        self.move_time(x_time, y_time, x_speed, y_speed)

        # Now that we know our position with certainty, move back to the center
        y_time = self.range_y_top / y_speed
        x_time = x_time / 2
        self.move_time(x_time, y_time, -x_speed, -y_speed)

    def __del__(self):
        self.close()


# Helper class for debugging without controlling an actual gimbal
class PsoudoGimbal:
    def __init__(self):
        pass

    def get_position(self):
        return 0, 0

    def get_delayed_position(self):
        return 0, 0

    def stop(self):
        pass

    def set_speeds_degs(self, x, y):
        pass

    def close(self):
        pass
