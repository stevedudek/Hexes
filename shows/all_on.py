from HelperFunctions import HEX_OFFSET
from color import random_color


class AllOn(object):
    def __init__(self, hexmodel):
        self.name = "AllOn"
        self.hexes = hexmodel
        self.color = random_color()
        self.speed = 0.2

    def next_frame(self):

        while True:

            self.hexes.set_all_cells(self.color)
            yield self.speed
