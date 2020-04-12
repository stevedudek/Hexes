from color import gradient_wheel, random_color, change_color, hue_to_color, random_hue, random_color_range
from random import random, choice, randint

import HelperFunctions as helpfunc


class Drop(object):
    def __init__(self, hexmodel, main_color, main_bands):
        self.hexes = hexmodel
        self.color = random_color_range(main_color, 0.1)
        self.bands = main_bands
        self.center = self.hexes.rand_cell()
        self.size = randint(0,5)  # Random drop size
        self.current_size = 0

    def increase_size(self):
        self.current_size += 1
        return self.current_size > self.size  # True if drop is fully drawn

    def draw_drop(self):
        if self.current_size == 0:  # just draw the center
            self.hexes.set_cell(self.center, self.color)
        else:
            self.hexes.set_cells(helpfunc.hex_ring(self.center, self.current_size),
                                 change_color(self.color, 0.008 * self.current_size * self.bands))


class RainDrops(object):
    def __init__(self, hexmodel):
        self.name = "rain drops"
        self.hexes = hexmodel
        self.drops = []  # List that holds Drop objects
        self.speed = 0.1
        self.main_color = random_color()
        self.main_bands = randint(2, 10)  # Change in color between rings

    def next_frame(self):

        while True:

            if not self.drops or helpfunc.one_in(3):
                self.drops.append(Drop(self.hexes, self.main_color, self.main_bands))

            # Draw all the drops
            # Increase the size of each drop - kill a drop if at full size
            for drop in self.drops:
                drop.draw_drop()
                if drop.increase_size():
                    self.drops.remove(drop)

            yield self.speed  	# random time set in init function

