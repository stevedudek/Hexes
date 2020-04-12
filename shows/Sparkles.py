from color import gradient_wheel, random_color, change_color, hue_to_color, random_hue, random_color_range
from random import random, choice, randint

import HelperFunctions as helpfunc


class Sparkle(object):
    def __init__(self, hexmodel, pos, color):
        self.hexes = hexmodel
        self.pos = pos
        self.color = color
        self.intense = 0
        self.growing = True

    def draw_sparkle(self):
        if self.hexes.cell_exists(self.pos):
            self.hexes.set_cell(self.pos, gradient_wheel(self.color, self.intense))

    def fade_sparkle(self):
        if helpfunc.one_in(2):
            if self.growing:
                self.intense += 0.25
                if self.intense >= 1.0:
                    self.intense = 1
                    self.growing = False
                return True
            else:
                self.intense -= 0.25
                return self.intense > 0


class Sparkles(object):
    def __init__(self, hexmodel):
        self.name = "Sparkles"
        self.hexes = hexmodel
        self.sparkles = []	# List that holds Sparkle objects
        self.speed = 1.0 / randint(5, 50)
        self.color = random_color()
        self.spark_num = 30 * helpfunc.NUM_HEXES

    def next_frame(self):

        self.sparkles = [Sparkle(self.hexes, pos=self.hexes.rand_cell(), color=self.color)
                         for _ in range(self.spark_num)]

        while True:

            while len(self.sparkles) < self.spark_num:
                self.sparkles.append(Sparkle(self.hexes, pos=self.hexes.rand_cell(), color=self.color))

            self.hexes.black_all_cells()

            # Draw the sparkles
            for sparkle in self.sparkles:
                sparkle.draw_sparkle()
                if not sparkle.fade_sparkle():
                    self.sparkles.remove(sparkle)

            if helpfunc.one_in(5):
                self.color = change_color(self.color, 0.02)

            yield self.speed  # random time set in init function
