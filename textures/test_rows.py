from HelperFunctions import HEX_OFFSET
from color import random_color


class TestRows(object):
    def __init__(self, hexmodel):
        self.name = "TestRows"        
        self.hexes = hexmodel
        self.row = -5
        self.color = random_color()
        self.speed = 1

    def next_frame(self):

        while True:

            self.hexes.black_all_cells()
            cells = [(0, self.row, y) for y in range(-HEX_OFFSET, HEX_OFFSET + 1)]
            self.hexes.set_cells(cells, self.color)

            self.row += 1
            if self.row > HEX_OFFSET:
                self.row = -HEX_OFFSET

            yield self.speed
