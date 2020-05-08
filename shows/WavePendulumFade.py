from HelperFunctions import*
from math import sin, cos, pi
from color import random_color, random_color_range, change_color
import hex as hex


class WavePendulumFade(object):
    def __init__(self, hexmodel):
        self.name = "WavePendulumFade"
        self.hexes = hexmodel
        self.faders = Faders(hexmodel)
        self.speed = 0.01
        self.counter = 0
        self.color = rand_color()
        self.min_freq = 10	# fastest pendulum does this many cycles in one loop
        self.cycle_time = 8	 # speed of one cycle
        self.cycles = int(self.cycle_time / self.speed)
        self.gradient = 20
        self.width = hex.NUM_HEXES * hex.HEX_SIZE

    def next_frame(self):

        while True:

            self.hexes.black_all_cells()

            for y in range(hex.HEX_SIZE):

                w = (self.min_freq + y) / float(self.cycles) # pendulum frequency
                x = int((cos(w * self.counter) + 1) * self.width / 2)
                h = x // hex.HEX_SIZE
                hex_x = x % hex.HEX_SIZE

                self.faders.add_fader(change_color(self.color, y * self.gradient / 1500.0),
                                      (h, hex_x - hex.HEX_OFFSET, y - hex.HEX_OFFSET),
                                      intense=1.0, growing=False, change=0.05)

            self.faders.cycle_faders()

            self.counter += 1

            if self.counter % (int(2 * pi * self.cycles)) == 0:
                self.color = random_color_range(self.color, 0.15)
                self.gradient = up_or_down(self.gradient, 5, 15, 40)

            yield self.speed  	# random time set in init function