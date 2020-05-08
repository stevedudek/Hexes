from HelperFunctions import*
from math import sin, cos, pi
from color import random_color, random_color_range, change_color, rgb_to_hsv, dim_color, black
import hex as hex


class WavePendulumFilled(object):
    def __init__(self, hexmodel):
        self.name = "WavePendulumFilled"
        self.hexes = hexmodel
        self.speed = 0.05
        self.counter = 0
        self.color = rand_color()
        self.min_freq = 10  # fastest pendulum does this many cycles in one loop
        self.cycle_time = 5	 # speed of one cycle
        self.cycles = int(self.cycle_time / self.speed)
        self.gradient = 10
        self.up_down = True
        self.width = hex.NUM_HEXES * hex.HEX_SIZE

    def next_frame(self):

        while True:

            for x in range(self.width):

                w = (self.min_freq + x) / float(self.cycles)  # pendulum frequency
                y_top = (cos(w * self.counter) + 1) * hex.HEX_SIZE / 2

                for y in range(hex.HEX_SIZE):
                    if self.up_down:
                        c = change_color(self.color, x * self.gradient / 1500.0) if y < y_top else black()
                    else:
                        c = change_color(self.color, x * self.gradient / 1500.0) if y > y_top else black()
                    h = x // hex.HEX_SIZE
                    hex_x = x % hex.HEX_SIZE

                    self.hexes.set_cell((h, hex_x - hex.HEX_OFFSET, y - hex.HEX_OFFSET), dim_color(c, 0.5))

            self.counter += 1
            if self.counter % (int(2 * pi * self.cycles)) == 0:
                self.min_freq = up_or_down(self.min_freq, 1, 3, 10)
                self.gradient = up_or_down(self.gradient, 2, 5, 15)
                self.color = random_color_range(self.color, 0.007)
                self.up_down = not self.up_down

            yield self.speed  # random time set in init function