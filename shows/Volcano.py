from color import random_hue, hue_to_color, random_color, black, gradient_wheel, rgb_to_hsv, random_color_range
from random import random, randint, choice

import HelperFunctions as helpfunc


class Rock(object):
    def __init__(self, hexmodel, h, main_color):
        self.hexes = hexmodel
        self.h = h
        self.color = random_color_range(main_color, 0.1)
        self.direction = choice((0, 1, 1.5, 2, 3))
        self.pos = helpfunc.get_center(self.h)
        self.life = randint(5, 15)  # How long the rock is around
        self.boulder = 0

        if helpfunc.one_in(10):
            self.boulder = 1

    def draw_rock(self):
        self.hexes.set_cell(self.pos, self.color)

        # boulder are bigger - one additional ring
        if self.boulder == 1:
            self.hexes.set_cells(helpfunc.hex_ring(self.pos, 1), self.color)

    def move_rock(self):
        self.pos = self.hex_in_dirs(self.pos, self.direction)  # Where is the rock moving?

        # Angle the rock downward
        if helpfunc.one_in(3):
            if self.direction == 1.5:  # Heading upwards
                self.direction = 1 + (randint(0, 2) / 2.0)
            elif self.direction == 0:
                self.direction = 5
            elif self.direction == 1:
                self.direction = 0
            elif self.direction == 2:
                self.direction = 3
            elif self.direction == 3:
                self.direction = 4
            elif self.direction == 4:
                self.direction = 4.5
            elif self.direction == 5:
                self.direction = 4.5

        self.life -= 1
        return self.life > 0

    def wiggle_drop(self):
        self.direction = 4 + (randint(0, 2) / 2.0)

    @staticmethod
    def hex_in_dirs(coord, direction):
        """
        Returns the coordinates of the hex one pixel from a given hex.
        Direction is indicated by an integer, with two possible half-integers:
        1.5 = straight up
        4.5 = straight down

         2  /1.5\  1
         3 |     | 0
         4  \4.5/  5
        """
        h, x, y = coord

        if direction == 1.5:  # Need to split 1.5 into 1 & 2
            direction = 1 if y % 2 else 2
        if direction == 4.5:  # Need to split 4.5 into 4 & 5
            direction = 5 if y % 2 else 4

        return helpfunc.hex_in_direction(coord, int(direction))


class Volcano(object):
    def __init__(self, hexmodel):
        self.name = "Volcano"
        self.hexes = hexmodel
        self.rocks = []  # List that holds rocks
        self.rock_intense = [randint(3,8) for _ in helpfunc.all_hexes()]  # Lower = more rocks
        self.lava_color = random_color(reds=True)
        self.volcano_color = rgb_to_hsv((100, 100, 100)) 		# Grey: (x,x,x)
        self.background_color = black()
        self.speed = 0.05 * randint(1, 5)
        self.clock = 0

    def draw_volcano(self):
        volcano_lines = ( ((0, 1), 4, 6), ((1, 1), 4, 5), ((2, 1), 4, 5), ((3, 1), 4, 5),
                          ((4, 1), 4, 6), ((5, 1), 4, 1), ((1, 5), 4, 2))

        for h in helpfunc.all_hexes():
            for line in volcano_lines:
                start, direction, distance = line
                x, y = start
                self.hexes.set_cells(helpfunc.hex_line_in_direction((h, x, y), direction, distance), self.volcano_color)
  
    def next_frame(self):

        while (True):

            # Start new rocks
            for h in helpfunc.all_hexes():
                if helpfunc.one_in(self.rock_intense[h]):
                    self.rocks.append(Rock(self.hexes, h, self.lava_color))

            # Background the screen - occasionally set to lava red
            if helpfunc.one_in(100):
                self.hexes.set_all_cells(rgb_to_hsv((200, 0, 0)))
            else:
                self.hexes.black_all_cells()

            self.draw_volcano()

            # Draw all the rocks
            for rock in self.rocks:
                rock.draw_rock()
                if not rock.move_rock():  # Is rock dead?
                    self.rocks.remove(rock)

            self.clock += 1
            for h in helpfunc.all_hexes():
                if helpfunc.one_in(20):
                    self.rock_intense[h] = helpfunc.up_or_down(self.rock_intense[h], 1, 3, 8)

            if self.clock > 100:
                self.clock = 0

            if helpfunc.one_in(10):
                self.lava_color = random_color_range(self.lava_color, 0.05)

            yield self.speed
