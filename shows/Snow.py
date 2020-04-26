from color import gradient_wheel, random_color, change_color, hue_to_color, white, rgb_to_hsv
from random import random, choice, randint

import HelperFunctions as helpfunc


class Snow(object):
    def __init__(self, hexmodel, direction):
        self.hexes = hexmodel
        self.color = white()
        self.direction = direction
        self.pos = self.pick_start_rain_spot()
        self.life = 50  # How long a flake lives

    def draw_snow(self):
        self.hexes.set_cell(self.pos, self.color)

    def move_snow(self):
        new_spot = helpfunc.hex_in_direction(self.pos, self.direction)  # Where is the snow falling?
        if self.hexes.cell_exists(new_spot):  # Is new spot off the board?
            self.pos = new_spot  # On board. Update spot

        self.life -=1
        return self.life > 0

    def set_pos(self, pos):
        self.pos = pos

    def pick_start_rain_spot(self):
        while True:
            start_spot = choice(helpfunc.hex_ring(helpfunc.get_random_center(), 5))  # Starting position on outside ring
            h, x, y = start_spot
            if x + y < 1:  # Approximately the top half of display
                return start_spot


class Flake(object):
    def __init__(self, hexmodel):
        self.hexes = hexmodel
        self.color = white()
        self.line = []  # List that holds flake lines

    def move_flake(self):
        if len(self.line) < helpfunc.NUM_HEXES:
            self.build_flake()
        else:
            for line in self.line:
                line.wiggle_line()

    def draw_flake(self):
        for line in self.line:
            line.draw_mirrored_line()

    def build_flake(self):
        # Spoke line
        spoke = randint(1, 6)
        first_line = Lines(self.hexes, start=helpfunc.get_random_center(), direction=0, length=spoke, color=white())
        self.line.append(first_line)

        # 2nd line
        spoke2 = randint(0, spoke)
        if first_line.get_line():
            second_line = Lines(self.hexes, start=choice(first_line.get_line()), direction=1, length=spoke2,
                                color=rgb_to_hsv((250, 250, 255)))
            self.line.append(second_line)

            # 3rd line
            spoke3 = randint(0, spoke2)
            if second_line.get_line():
                third_line = Lines(self.hexes, start=choice(second_line.get_line()), direction=5, length=spoke3,
                                   color=rgb_to_hsv((245, 245, 255)))
                self.line.append(third_line)


class Lines(object):
    def __init__(self, hexmodel, start, direction, length, color):
        self.hexes = hexmodel
        self.start = start
        self.direction = direction
        self.length = length
        self.color = color

    def wiggle_line(self):
        if helpfunc.one_in(2):
            self.length = helpfunc.up_or_down(self.length, 1, 1, 6)
        else:
            h, x, y = self.start
            x = helpfunc.up_or_down(x, 1, 1, 6)
            self.start = (h, x, y)

    def draw_mirrored_line(self):
        """Draw mirrored line"""
        for coord in self.get_line():
            self.draw_mirrored_cell(coord, self.color)

    def get_line(self):
        """Get Line - returns the hexes along a line"""
        return helpfunc.hex_line_in_direction(self.start, self.direction, self.length)

    def draw_mirrored_cell(self, pos, color):
        """Draws a particular hex and its 5 mirrored positions as well"""
        self.hexes.set_cells(helpfunc.mirror_hexes(pos), color)


class Snows(object):
    
    def __init__(self, hexmodel):
        self.name = "Snow"        
        self.hexes = hexmodel
        self.drops = []  # List that holds Snow objects
        self.wind = (4 + randint(0, 2)) % 6
        self.speed = 1.0 / randint(5, 20)
        self.rain_intense = 1
        self.background = 100  # Background Blue
        self.clock = 0
        self.show_length = 200
        self.big_flake = Flake(self.hexes)

    def next_frame(self):

        while self.clock < self.show_length * 2:

            # Background the screen to a shade of blue

            self.hexes.set_all_cells(rgb_to_hsv((0, 0, self.background)))

            # Which sub-show are we in?

            if self.clock > self.show_length:  # in show: Snow Fall

                for i in range(self.rain_intense * helpfunc.NUM_HEXES):
                    self.drops.append(Snow(self.hexes, self.wind))

                # Draw all the snow
                for drop in self.drops:
                    drop.draw_snow()
                    if not drop.move_snow():  # Drop off screen
                        self.drops.remove(drop)

            else:  # in show: Big Flake
                self.big_flake.move_flake()
                self.big_flake.draw_flake()

            self.clock += 1

            if self.clock >= self.show_length * 2:
                self.clock = 0

            # Randomly change the wind direction, speed and drop length

            if helpfunc.one_in(100):
                self.wind = (4 + randint(0,2)) % 6

            if helpfunc.one_in(100):
                self.rain_intense = helpfunc.up_or_down(self.rain_intense, 1, 1, 5)

            if helpfunc.one_in(50):
                self.speed = helpfunc.up_or_down(self.speed, 0.05, 0.05, 0.5)

            # Randomly change the colors

            if helpfunc.one_in(50):
                self.background = helpfunc.up_or_down(self.background, 4, 50, 255)

            yield self.speed