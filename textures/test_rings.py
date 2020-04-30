from color import random_hue, hue_to_color, random_color, black, gradient_wheel, rgb_to_hsv, random_color_range
from random import random, randint, choice

import HelperFunctions as helpfunc


class TestRings(object):
    def __init__(self, hexmodel):
        self.name = "TestRings"        
        self.hexes = hexmodel
        self.ring_number = 0
        self.ring_color = random_color()
        self.speed = 1.0  # 0.1 * randint(1, 6)

    def next_frame(self):

        while True:

            self.hexes.black_all_cells()

            for h in helpfunc.all_hexes():
                ring_size = (self.ring_number + (h * 2)) % 6
                self.hexes.set_cells(helpfunc.hex_ring(helpfunc.get_center(h), ring_size),
                                     self.ring_color)

            self.ring_number = (self.ring_number + 1) % 6

            if helpfunc.one_in(10):
                self.ring_color = random_color_range(self.ring_color, 0.05)

            yield self.speed


