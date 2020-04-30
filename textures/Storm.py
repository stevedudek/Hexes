from color import gradient_wheel, random_color, change_color, hue_to_color, white, rgb_to_hsv
from random import random, choice, randint

import HelperFunctions as helpfunc


class Raindrop(object):
    def __init__(self, hexmodel, color, direction):
        self.hexes = hexmodel
        self.color = color
        self.direction = direction
        self.pos = self.pick_start_rain_spot()

    def draw_drop(self):
        self.hexes.set_cell(self.pos, self.color)

    def move_drop(self):
        new_spot = helpfunc.hex_in_direction(self.pos, self.direction)  # Where is the snow falling?
        if self.hexes.cell_exists(new_spot):  # Is new spot off the board?
            self.pos = new_spot  # On board. Update spot
            return True
        return False

    def set_pos(self, pos):
        self.pos = pos

    def wiggle_drop(self):
        wiggle_direction = 5 if helpfunc.one_in(2) else 1
        self.direction = (self.direction  + wiggle_direction ) % 6

    @staticmethod
    def pick_start_rain_spot():
        while True:
            start_spot = choice(helpfunc.hex_ring(helpfunc.get_random_center(), 5))  # Starting position on outside ring
            h, x, y = start_spot
            if x + y < 0:  # Approximately top third of display
                return start_spot


class Storm(object):
    def __init__(self, hexmodel):
        self.name = "Storm"        
        self.hexes = hexmodel
        self.drops = []  # List that holds Raindrop objects
        self.bolts = []  # List that holds Lighting bolts
        self.wind = (4 + randint(0, 2)) % 6
        self.speed = 0.1
        self.drop_length = 2
        self.rain_intense = helpfunc.NUM_HEXES
        self.rain_hue = 235  # Grey
        self.rain_color = rgb_to_hsv((self.rain_hue, self.rain_hue, self.rain_hue))
        self.background_hue = 15
        self.background_color = rgb_to_hsv((self.background_hue, self.background_hue, self.background_hue))
        self.clock = 0

    def next_frame(self):

        while True:

            for _ in range(self.rain_intense):
                if len(self.drops) <= self.clock / (20 * helpfunc.NUM_HEXES):
                    self.drops.append(Raindrop(hexmodel=self.hexes, color=self.rain_color, direction=self.wind))

            self.hexes.set_all_cells(self.background_color)

            # Draw all the drops
            for drop in self.drops:
                for _ in range(self.drop_length):
                    drop.draw_drop()
                    if not drop.move_drop():  # Drop off screen
                        self.drops.remove(drop)
                        break

            self.clock = (self.clock + 1) % 100

            # Randomly change the wind direction and drop length

            if helpfunc.one_in(100):
                self.wind = (4 + randint(0,2)) % 6

            if helpfunc.one_in(100):
                self.drop_length = helpfunc.up_or_down(self.drop_length, 1, 1, 3)

            if helpfunc.one_in(100):
                self.rain_intense = helpfunc.up_or_down(self.rain_intense, 1, 1, 5)

            # Randomly change the colors

            if helpfunc.one_in(50):
                self.rain_hue = helpfunc.up_or_down(self.rain_hue, 4, 220, 255)
                self.rain_color = rgb_to_hsv((self.rain_hue, self.rain_hue, self.rain_hue))

            if helpfunc.one_in(50):
                self.background_hue = helpfunc.up_or_down(self.background_hue, 4, 0, 50)
                self.background_color = rgb_to_hsv((self.background_hue, self.background_hue, self.background_hue))

            # draw flash lighting

            if helpfunc.one_in(100):
                self.hexes.set_all_cells(rgb_to_hsv((255, 255, 127)))
                yield 0.3

            # draw bolt lighting - a bolt is just a quickly-moving raindrop that does not erase

            if helpfunc.one_in(50):

                # set background to dark blue
                self.hexes.set_all_cells(rgb_to_hsv((0, 0, 127)))  # Dark blue background
                yield 0.05

                for _ in range(randint(1 * helpfunc.NUM_HEXES, 3 * helpfunc.NUM_HEXES)):  # number of lighting bolts
                    self.bolts.append(Raindrop(hexmodel=self.hexes, color=rgb_to_hsv((255, 255, 0)), direction=5))

                for _ in range(10):  # bolt length
                    yield 0.05

                    # draw all the bolts
                    for bolt in self.bolts:
                        bolt.draw_drop()
                        if helpfunc.one_in(8):
                            branch = Raindrop(hexmodel=self.hexes, color=rgb_to_hsv((255, 255, 0)), direction=5)
                            branch.set_pos(branch.pos)
                            branch.wiggle_drop()
                            self.bolts.append(branch)
                        if helpfunc.one_in(5):
                            bolt.wiggle_drop()
                        if not bolt.move_drop():  # Drop off screen
                            self.bolts.remove(bolt)

                    yield 0.05

                self.bolts = []  # need to clear bolts

            yield self.speed
