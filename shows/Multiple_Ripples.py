from random import random, randint, choice
from color import random_hue, hue_to_color, random_color, black, change_color, random_color_range, gradient_wheel

import HelperFunctions as helpfunc


class Ripple(object):
    def __init__(self, hexmodel, hex_number=None):
        self.hexes = hexmodel
        self.center = hexmodel.rand_cell(hex_number)
        self.lifetime = randint(20, 100)  # Time ripple lives

    def draw(self, color, time, width):
        self.hexes.set_cell(self.center, gradient_wheel(color, self.get_att(width, 0, time)))

        # Draw the rings
        for i in range(20):  # total number of rings - can be bigger than display
            self.hexes.set_cells(helpfunc.hex_ring(self.center, i),
                                 gradient_wheel(color, self.get_att(width, i, time)))

    @staticmethod
    def get_att(width, ring, time):
        saw = (1.0 / width) * (ring + ((100000 - time) % 30))  # Linear sawtooth
        while saw >= 2:
            saw -= 2.0  # Cut into sawtooth periods
        if saw > 1:
            saw = 2.0 - saw  # Descending part of sawtooth
        return saw

    def decrease_time(self):
        self.lifetime -= 1
        return self.lifetime > 0


class MultipleRipples(object):
    def __init__(self, hexmodel):
        self.name = "MultipleRipples"
        self.hexes = hexmodel
        self.ripples = []  # List that holds Ripple objects
        self.time = 0
        self.speed = 0.1 + (random() / 2)
        self.width = randint(8, 20)
        self.color = random_color()

    def next_frame(self):

        self.ripples = [Ripple(self.hexes, h) for h in helpfunc.all_hexes()]

        while True:

            # Check how many rips are in play
            # If no rips, add one. If rips < 6 then add one more randomly
            if len(self.ripples) < 6 * helpfunc.NUM_HEXES and helpfunc.one_in(20):
                self.ripples.append(Ripple(self.hexes))

            for ripple in self.ripples:
                ripple.draw(self.color, self.time, self.width)

            # Slowly change the colors
            if helpfunc.one_in(10):
                self.color = change_color(self.color, 0.07)

            # Decrease the life of each ripple - kill a ripple if life is zero
            for ripple in self.ripples:
                if not ripple.decrease_time():
                    self.ripples.remove(ripple)

            self.time += 1

            yield self.speed  # random time set in init function


