from math import sin
from color import random_hue, hue_to_color, random_color, black, gradient_wheel, rgb_to_hsv
from random import random, randint, choice

import HelperFunctions as helpfunc


def get_cell(coord):
    h, x, y = coord
    x = int(x)
    y = int(y)

    if x == 0:
        return (h, 0, y)
    elif x > 0:
        hex1 = helpfunc.hex_in_direction((h, 0, y), 1, (x / 2) + (x % 2))
        return helpfunc.hex_in_direction(hex1, 0, x / 2)
    else:
        x *= -1
        hex1 = helpfunc.hex_in_direction((h, 0, y), 3, (x / 2) + (x % 2))
        return helpfunc.hex_in_direction(hex1, 4, x / 2)


def get_box(coord, width, height):
    """Returns a list of cells within an box (x,y coord of the lower left corner)"""
    h, x, y = coord
    return [get_cell((h, x + dx, y + dy)) for dx in range(width) for dy in range(height)]


def get_triangle(coord, length, width):
    """Returns a list of cells within an upright triangle or trapezoid
    (x,y coord of the lower left corner), length of edge, width of trapezoid (0 = triangle)"""
    current = coord
    cells = []

    for w in range(width):
        for l in range(length):
            cells.append(helpfunc.hex_in_direction(current, 1, l))  # 2 is up
        length -= 1
        length = max([length, 0])
        current = helpfunc.hex_in_direction(current, 1, 1)
        current = helpfunc.hex_in_direction(current, 0, 1)

    return cells


class Stuff(object):
    def __init__(self, hexmodel, h):
        """Subclass all this!"""
        self.hexes = hexmodel
        self.h = h  # hex_number
        self.x_coord = 7.0  # right off the board
        self.y_coord = 0.0  # default changed by subclass
        self.speed = 0

    def draw_stuff(self, clock):
        """Subclass!"""
        return

    def move_stuff(self, car_speed):
        stuff_speed = (self.y_coord + car_speed) / 7.0
        self.x_coord -= stuff_speed
        return self.x_coord >= -20

    def get_level(self):
        return self.y_coord + 6

    def draw_line(self, start, direction, length, color):
        self.hexes.set_cells(helpfunc.hex_line_in_direction(coord=start, direction=direction, distance=length), color)


class Tree(Stuff):
    def __init__(self, hexmodel, h):
        super(Tree, self).__init__(hexmodel, h)
        self.y_coord = randint(0, 5)
        self.color = rgb_to_hsv((0, randint(100, 255), 0))  # Some sort of green
        self.trunk = rgb_to_hsv((randint(40, 60), 0, 0))  # Dark Brown

    def draw_stuff(self, clock):
        pos = get_cell((self.h, self.x_coord, self.y_coord))

        # Draw leaves
        leaf_top = helpfunc.hex_in_direction(pos, 2, 2)

        self.hexes.set_cell(leaf_top, self.color)  # Draw the center
        self.hexes.set_cells(helpfunc.hex_ring(leaf_top, 1), self.color)  # Tree bulb
        if self.y_coord > 2:
            self.hexes.set_cells(helpfunc.hex_ring(leaf_top, 2), self.color)  # Bigger bulb

        self.hexes.set_cell(helpfunc.hex_in_direction(pos, 2, 1), self.trunk)
        self.hexes.set_cell(pos, self.trunk)


class RedTree(Tree):
    def __init__(self, hexmodel, h):
        super(RedTree, self).__init__(hexmodel, h)
        red = randint(200, 255)
        self.color = rgb_to_hsv((randint(200, 255), randint(0, red), 0))  # Some sort of yellow/red


class Mountain(Stuff):
    def __init__(self, hexmodel, h):
        super(Mountain, self).__init__(hexmodel, h)
        self.y_coord = 0
        self.gray = randint(50, 100)
        self.size = randint(4, 10)

    def draw_stuff(self, clock):
        pos = get_cell((self.h, self.x_coord, self.y_coord))
        color = rgb_to_hsv((self.gray, self.gray, self.gray))

        self.hexes.set_cells(get_triangle(pos, self.size, self.size), color)


class House(Stuff):
    def __init__(self, hexmodel, h):
        super(House, self).__init__(hexmodel, h)
        self.y_coord = randint(0, 6)
        self.roof = random_color()
        self.wall = random_color()

    def draw_stuff(self, clock):
        pos = get_cell((self.h, self.x_coord, self.y_coord))

        width = (self.y_coord / 2) + 2
        height = (self.y_coord / 2) + 1
        self.hexes.set_cells(get_box(pos, width, height), self.wall)

        hex1 = helpfunc.hex_in_direction(pos, 2, height)
        roof_corner = helpfunc.hex_in_direction(hex1, 4, 1)
        self.hexes.set_cells(get_triangle(roof_corner, height+1, width), self.roof)


class Bird(Stuff):
    def __init__(self, hexmodel, h):
        super(Bird, self).__init__(hexmodel, h)
        self.y_coord = randint(-6, 6)
        self.color = black()
        self.x_dir = randint(-1, 1)
        self.y_dir = randint(-1, 1)

    def draw_stuff(self, clock):
        pos = get_cell((self.h, self.x_coord, self.y_coord))

        self.hexes.set_cell(pos, self.color)  # Draw the center

        if clock % 2:
            self.hexes.set_cell(helpfunc.hex_in_direction(pos, 0, 1), self.color)
            self.hexes.set_cell(helpfunc.hex_in_direction(pos, 4, 1), self.color)
        else:
            self.hexes.set_cell(helpfunc.hex_in_direction(pos, 3, 1), self.color)
            self.hexes.set_cell(helpfunc.hex_in_direction(pos, 1, 1), self.color)

    def get_level(self):
        return 12  # Override here draws birds on top of everything

    def move_stuff(self, car_speed):
        stuff_speed = 0.5
        self.x_coord -= stuff_speed
        self.x_coord -= (self.x_dir / 2.0)
        self.y_coord -= (self.y_dir / 2.0)

        if helpfunc.one_in(6):
            self.x_dir = randint(-1, 1)
            self.y_dir = randint(-1, 1)

        return self.x_coord >= -20


class Cloud(Stuff):
    def __init__(self, hexmodel, h):
        super(Cloud, self).__init__(hexmodel, h)
        self.y_coord = randint(-6, -2)
        self.gray = randint(220, 255)
        self.wind = 0.1

    def draw_stuff(self, clock):
        pos = get_cell((self.h, self.x_coord, self.y_coord))
        color = rgb_to_hsv((self.gray, self.gray, self.gray))

        # Draw two lines
        self.hexes.set_cells(helpfunc.hex_line_in_direction(pos, 1, 1), color)
        hex1 = helpfunc.hex_in_direction(pos, 0, 1)
        self.hexes.set_cells(helpfunc.hex_line_in_direction(hex1, 1, 1), color)

    def move_stuff(self, car_speed):
        self.x_coord -= self.wind
        return self.x_coord >= -10


class Driving(object):
    def __init__(self, hexmodel):
        self.name = "Driving"
        self.hexes = hexmodel
        self.stuffs = []  # List that holds stuffs objects
        self.sky_color = black()  # Set for each season
        self.ground_color = rgb_to_hsv((255, 255, 0))  # Set for each season
        self.cars_speed = 1.0  # How fast the scene moves
        self.clock = 0
        self.scene = 0
        self.max_scene = 6

    def next_frame(self):

        self.set_colors()

        while True:

            self.generate_stuffs()
            self.move_stuffs()
            self.draw_ground()
            self.draw_stuffs()

            self.clock += 1
            if self.clock % 1000 == 0:
                self.scene += 1
                self.scene = self.scene % self.max_scene
                self.set_colors()
            if self.clock > 10000:
                self.clock = 0
            self.cars_speed = sin(self.clock / (64 * 3.14159)) + 1.0

            yield 0.05

    def move_stuffs(self):
        for stuff in self.stuffs:
            if not stuff.move_stuff(self.cars_speed):
                self.stuffs.remove(stuff)

    def draw_stuffs(self):
        # draw further away things first
        for distance in range(12):
            for stuff in self.stuffs:
                if stuff.get_level() == distance:
                    stuff.draw_stuff(self.clock)

    def draw_ground(self):
        self.hexes.set_all_cells(self.sky_color)
        for h in helpfunc.all_hexes():
            self.hexes.set_cells(get_box((h, -5, 1), 11, 6), self.ground_color)

    def generate_stuffs(self):
        kinds = [Tree, RedTree, Mountain, House, Bird, Cloud]

        freq = [ [10,0,2,2,0,0],
                 [1,10,5,0,2,0],
                 [2,0,1,10,0,0],
                 [0,3,10,0,20,0],
                 [5,0,0,2,0,0],
                ]

        for h in helpfunc.all_hexes():
            for obj in range(len(kinds)):
                if randint(0, 100) < freq[self.scene][obj]:
                    if kinds[obj] in [House]:
                        self.stuffs.append(kinds[obj](self.hexes, h))

        #if len(self.stuffs) < 20:
        #	if randint(0,5) == 1:
        #		new_mountain = Mountain(self.hexes)
        #		self.stuffs.append(new_mountain)
        #	else:
        #		new_tree = Bird(self.hexes)
        #		self.stuffs.append(new_tree)


    def set_colors(self):

        skies = [(0,0,200), (50,50,255), (0,0,255), (0,0,100), (100,100,255)]
        grounds = [(255,255,0), (200,255,0), (0,25,0), (200,200,0), (100,200,0)]

        self.sky_color = rgb_to_hsv(skies[self.scene])
        self.ground_color = rgb_to_hsv(grounds[self.scene])
