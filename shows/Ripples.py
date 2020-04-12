from color import gradient_wheel, random_color, change_color, hue_to_color, random_hue, random_color_range
from random import random, choice, randint

import HelperFunctions as helpfunc


class Ripples(object):
    def __init__(self, hexmodel):
        self.name = "Ripples"        
        self.hexes = hexmodel
        self.centers = [self.hexes.rand_cell(h) for h in helpfunc.all_hexes()]
        self.time = 0
        self.speed = 0.1 + (random() / 2)
        self.width = [randint(8, 20) for _ in range(helpfunc.NUM_HEXES)]
        self.color = [random_color() for _ in range(helpfunc.NUM_HEXES)]
    
    def get_att(self, width, ring, time):
        saw = (1.0 / width) * (ring + ((100000 - time) % 30))	# Linear sawtooth
        while saw >= 2:
            saw = saw - 2  # Cut into sawtooth periods
        if saw > 1:
            saw = 2 - saw  # Descending part of sawtooth
        return saw

    def next_frame(self):

        while True:

            for h in helpfunc.all_hexes():

                self.hexes.set_cell(self.centers[h],
                                    gradient_wheel(self.color[h], self.get_att(self.width[h], 0, self.time)))

                # Draw the rings
                for ring in range(15):  # total number of rings - can be bigger than display
                    color = gradient_wheel(self.color[h], self.get_att(self.width[h], ring, self.time))
                    self.hexes.set_cells(helpfunc.hex_ring(self.centers[h], ring), color)

                # Slowly change the colors
                if helpfunc.one_in(4):
                    self.color[h] = change_color(self.color[h], 0.05)

                # Move the center of the ripple like a drunken mason
                if helpfunc.one_in(5):
                    while True:
                        new_hex = choice(helpfunc.neighbors(self.centers[h]))
                        if self.hexes.cell_exists(new_hex):
                            self.centers[h] = new_hex
                            break

            self.time += 1

            yield self.speed  # random time set in init function

