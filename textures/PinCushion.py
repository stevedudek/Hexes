from math import exp, sin, radians
from random import randint
from color import change_color, gradient_wheel, random_color
import HelperFunctions as helpfunc


class PinCushion(object):
    def __init__(self, hexmodel):
        self.name = "Pin Cushion"
        self.hexes = hexmodel
        self.pos = []  # List of pin centers
        self.space = 0
        self.time = 0
        self.speed = 0.1
        self.width = randint(8, 20)
        self.color = random_color()
        self.a = 1  # -1 < a < 1 : sign and intensity of well
        self.c = 5  # Width of well
        self.min_bright = 0.1

    def next_frame(self):

        while True:

            if self.time == 0:
                self.pos = self.get_pin_centers(randint(3, 10))
                self.c = randint(2, 5)  # Width of well

            self.hexes.set_all_cells(self.color)

            # Draw the rings
            for ring in range(12, 0, -1): # total number of rings - can be bigger than display
                for center in self.pos:
                    h, x, y, = center
                    x = self.gauss(self.a, self.c, ring + 1, h)
                    atten = 1 + x if x < 0 else x
                    if abs(atten) < self.min_bright:
                        atten = self.min_bright
                    color = gradient_wheel(self.color, atten)

                    self.hexes.set_cells(helpfunc.hex_ring(center, ring), color)

            # Draw the center hexes - Not included in the ring model
            for center in self.pos:
                h, x, y, = center
                x = self.gauss(self.a, self.c, ring + 1, h)
                atten = 1 + x if x < 0 else x
                if abs(atten) < self.min_bright:
                    atten = self.min_bright
                color = gradient_wheel(self.color, atten)

                self.hexes.set_cells(self.pos, color)

            if helpfunc.one_in(8):
                self.color = change_color(self.color, 0.1)

            self.time = (self.time + 4) % 720

            self.a = sin(radians(self.time))

            yield self.speed  # random time set in init function

    def get_pin_centers(self, spacing):

        center_array = helpfunc.all_centers()

        for h in helpfunc.all_hexes():
            for direction in helpfunc.all_dir():
                new_center = helpfunc.get_center(h)
                for i in range(2):
                    new_center = helpfunc.hex_in_direction(new_center, direction, spacing)
                    center_array.append(new_center)

        return center_array

    def gauss(self, a, c, x, h):
        if h > 0:
            a = sin(radians((self.time + int(h * 240 / (h+1)) + (x * 2)) % 240))
        return a * exp(- 1 * x * x / (2.0 * c * c))
