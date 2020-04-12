from color import rgb_to_hsv
from random import randint

from HelperFunctions import one_in, hex_ring, hex_in_direction
from hex import NUM_HEXES


class Candle(object):
    def __init__(self, hexmodel, bottom, height):
        self.hexes = hexmodel
        self.bottom = bottom
        self.height = height
        self.burn = randint(15,40)

    def get_height(self):
        return self.height

    def get_wick(self):
        return hex_in_direction(self.bottom, 2, self.height - 1)

    def draw_candle(self, candle_color, wind):

        # Draw glow
        glow_size = self.height / 2
        glow_cent = self.get_wick() if wind == 10 else hex_in_direction(self.get_wick(), wind)
        self.hexes.set_cell(glow_cent, rgb_to_hsv((200, 200, 0)))

        for rings in range(1, glow_size + 1):
            self.hexes.set_cells(hex_ring(glow_cent, rings), rgb_to_hsv((255 - (rings * 30),
                                                                         255 - (rings * 30),
                                                                         0)))

        # Draw wax
        self.draw_line(self.bottom, 2, self.height - 1, candle_color)
        self.draw_line(hex_in_direction(self.bottom, 4), 2, self.height, candle_color)
        self.draw_line(hex_in_direction(self.bottom, 0), 2, self.height, candle_color)

        # Draw Flame
        if one_in(2):
            self.hexes.set_cell(self.get_wick(), rgb_to_hsv((255, randint(125,255), 0)))

    def burn_candle(self):
        if one_in(self.burn):
            self.height -= 1
            return self.height >= 0
        return True

    def draw_line(self, start, direction, length, color):
        for i in range(length):
            self.hexes.set_cell(start, color)
            start = hex_in_direction(start, direction)


class Candles(object):
    def __init__(self, hexmodel):
        self.name = "Candles"
        self.hexes = hexmodel
        self.candles = []  # List that holds Candles objects
        self.speed = 0.1

    def tot_candles(self):
        return sum([candle.get_height() for candle in self.candles])

    def next_frame(self):

        while True:
            if not self.candles:
                for h in range(NUM_HEXES):
                    self.candles += [Candle(self.hexes, (h, 0, 5),  9),  # center candle
                                     Candle(self.hexes, (h, -3, 5),  6),  # left candle
                                     Candle(self.hexes, (h, 3, 2), 6)]  # center candle

            candle_gray = 255 * self.tot_candles() / (20.0 * NUM_HEXES)

            wind = randint(0, 5) if one_in(5) else 10

            self.hexes.black_all_cells()
            # self.hexes.set_all_cells(rgb_to_hsv((0, 0, candle_gray)))  # Set background to blue-ish

            for candle in self.candles:
                candle.draw_candle(rgb_to_hsv((candle_gray, candle_gray, candle_gray)), wind)
                if not candle.burn_candle():
                    self.candles.remove(candle)

            yield self.speed