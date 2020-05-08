from HelperFunctions import*
from math import sin, cos, pi
from color import random_color, random_color_range, change_color, dim_color
import hex as hex


class WavePendulum(object):
    def __init__(self, hexmodel):
        self.name = "WavePendulum"
        self.hexes = hexmodel
        self.speed = 0.05
        self.counter = 0
        self.background = rand_color()
        self.color = change_color(self.background, 0.5)
        self.min_freq = 10	 # fastest pendulum does this many cycles in one loop
        self.cycle_time = 5	 # speed of one cycle
        self.cycles = int(self.cycle_time / self.speed)
        self.gradient = 3

    def next_frame(self):

        while True:

            self.hexes.set_all_cells(dim_color(self.background, 0.3))

            for x in range(hex.NUM_HEXES * hex.HEX_SIZE):

                w = (self.min_freq + x) / float(self.cycles)  # pendulum frequency
                y = int((cos(w * self.counter) + 1) * hex.HEX_SIZE / 2)
                h = x // hex.HEX_SIZE
                hex_x = x % hex.HEX_SIZE

                self.hexes.set_cell((h, hex_x - hex.HEX_OFFSET, y - hex.HEX_OFFSET),
                                    change_color(self.color, y * self.gradient / 1500.0))

            self.counter += 1
            if self.counter % (int(2 * pi * self.cycles)) == 0:
                self.min_freq = up_or_down(self.min_freq, 1, 3, 10)
                self.gradient = up_or_down(self.gradient, 1, 0, 10)
                self.color = change_color(self.color, 0.15)
                self.background = random_color_range(self.background, 0.015)

            yield self.speed