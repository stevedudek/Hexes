from random import random, randint, choice

from color import random_hue, gradient_wheel, hue_to_color
import HelperFunctions as helpfunc


class Trail(object):
    def __init__(self, hexmodel, color, intense, pos):
        self.hexes = hexmodel
        self.pos = pos
        self.h = self.pos[0]
        self.color = color
        self.intense = intense

    def draw_trail(self):
        self.hexes.set_cell(self.pos, gradient_wheel(hue_to_color(self.color), self.intense))

    def fade_trail(self):
        self.pos = helpfunc.get_close(self.pos, helpfunc.get_center(self.h))
        self.intense *= 0.7
        return self.intense > 0.05


class Planet(object):
    def __init__(self, hexmodel, pos, center, color, direction):
        self.hexes = hexmodel
        self.pos = pos
        self.color = color
        self.direction = direction
        self.center = center
        self.trails = []  # List that holds trails

    def draw_planet(self):

        self.fade_trails()

        self.draw_add_trail(self.color, 1, self.pos)  # Draw the center

        # Draw a middle ring
        for c in helpfunc.hex_ring(self.pos, 1):
            self.draw_add_trail(self.color, 0.9, c)

        # Draw an outer ring
        for c in helpfunc.hex_ring(self.pos, 2):
            self.draw_add_trail(self.color, 0.7, c)

    def move_planet(self):
        self.pos = helpfunc.clock_cell(self.pos, self.direction, self.center)
        self.color += 1

    def draw_add_trail(self, color, intense, pos):
        if self.hexes.cell_exists(pos):
            self.hexes.set_cell(pos, gradient_wheel(hue_to_color(color), intense))
            self.trails.append(Trail(self.hexes, color, intense, pos))

    def fade_trails(self):
        for trail in reversed(self.trails):	 # Plot last-in first
            trail.draw_trail()
            if not trail.fade_trail():
                self.trails.remove(trail)


class Circling(object):
    def __init__(self, hexmodel):
        self.name = "Circling"
        self.hexes = hexmodel
        self.planets = []  # List that holds Planet objects
        self.speed = 0.05
        self.color = random_hue()

    def next_frame(self):

        for h in helpfunc.all_hexes():
            center = helpfunc.get_center(h)
            color_offset = (self.color + 40) % 255
            self.planets += [Planet(self.hexes, (h, 0, 4), center, self.color, 1),
                             Planet(self.hexes, (h, 0, 4), center, color_offset, -1),
                             Planet(self.hexes, (h, 0, 2), center, self.color, 1),
                             Planet(self.hexes, (h, 0, 2), center, color_offset, -1),
                            ]

        while True:

            self.hexes.black_all_cells()

            for planet in self.planets:
                planet.draw_planet()
                planet.move_planet()

            self.color = (self.color + 1) % 255

            yield self.speed
