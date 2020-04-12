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
        self.intense -= 0.1
        return self.intense > 0


class Planet(object):
    def __init__(self, hexmodel, h, center, color, direction):
        self.hexes = hexmodel
        self.h = h
        self.pos = helpfunc.get_center(h)
        self.color = color
        self.direction = direction
        self.center = center
        self.trails = []  # List that holds trails

    def draw_planet(self):

        self.fade_trails()

        self.draw_add_trail(self.color, 1, self.pos)  # Draw the center

        # Draw an outer ring
        for cell in helpfunc.hex_ring(self.pos, 1):
            self.draw_add_trail(self.color, 0.9, cell)

    def move_planet(self):
        self.pos = helpfunc.clock_cell(self.pos, self.direction, self.center)
        self.center = helpfunc.clock_cell(self.center, -1, helpfunc.get_center(self.h))

    def draw_add_trail(self, color, intense, pos):
        if self.hexes.cell_exists(pos):
            self.hexes.set_cell(pos, gradient_wheel(hue_to_color(color), intense))
            self.trails.append(Trail(self.hexes, color, intense, pos))

    def fade_trails(self):
        for trail in reversed(self.trails):	 # Plot last-in first
            trail.draw_trail()
            if not trail.fade_trail():
                self.trails.remove(trail)


class Orbits(object):
    def __init__(self, hexmodel):
        self.name = "Orbits"
        self.hexes = hexmodel
        self.planets = []  # List that holds Planet objects
        self.speed = 0.05
        self.color = random_hue()

    def next_frame(self):

        for h in helpfunc.all_hexes():
            self.planets += [Planet(hexmodel=self.hexes, h=h, center=(h, 0, -2), color=self.color, direction=1),
                             Planet(hexmodel=self.hexes, h=h, center=(h, 0,  2), color=self.color, direction=1),
                             Planet(hexmodel=self.hexes, h=h, center=(h, 0, -4), color=self.color, direction=-1),
                             Planet(hexmodel=self.hexes, h=h, center=(h, 0,  4), color=self.color, direction=-1)]

        while True:

            # self.hexes.black_all_cells()

            for planet in self.planets:
                planet.draw_planet()
                planet.move_planet()

            self.color = (self.color + 1) % 255

            yield self.speed
