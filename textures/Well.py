from math import exp, sin, radians

from color import random_hue, hue_to_color, random_color, black, gradient_wheel, change_color
from random import random, randint, choice

import HelperFunctions as helpfunc


class Well(object):
    def __init__(self, hexmodel, h):
        self.name = "Well"
        self.hexes = hexmodel
        self.h = h
        self.pos = self.hexes.rand_cell(hex_number=h)
        self.direction = helpfunc.rand_dir()
        self.time = 0
        self.width = randint(8, 20)
        self.color = random_color()
        self.a = 1  # -1 < a < 1 : sign and intensity of well
        self.c = randint(2, 8)   # Width of well

    @staticmethod
    def gauss(a, c, x):
        return a * exp(- 1 * x * x / (2.0 * c * c))

    def draw(self):

        # Draw the center hex - Not included in the ring model
        x = self.gauss(self.a, self.c, 0)
        self.hexes.set_cell(self.pos, gradient_wheel(self.color, 1 + x))

        # Draw the rings
        for i in range(0, 15):  # total number of rings - can be bigger than display
            x = self.gauss(self.a, self.c, i + 1)
            self.hexes.set_cells(helpfunc.hex_ring(self.pos, i),
                                 gradient_wheel(self.color, 1 + x))

        self.time = (self.time + 16) % 720
        self.a = sin(radians(self.time))

        if helpfunc.one_in(8):
            self.color = change_color(self.color, 0.02)


class Wells(object):

    def __init__(self, hexmodel):
        self.name = "Wells"
        self.hexes = hexmodel
        self.wells = [Well(self.hexes, h) for h in helpfunc.all_hexes()]
        self.speed = 0.05 * randint(1, 4)

    def next_frame(self):

        while True:

            for well in self.wells:
                well.draw()

            yield self.speed  # random time set in init function
