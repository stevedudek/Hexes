from color import gradient_wheel, random_color, change_color, hue_to_color, random_hue
from random import random, choice, randint

from hex import NUM_HEXES
import HelperFunctions as helpfunc


class Bullet(object):
    def __init__(self, hexmodel, color, pos, direction=None):
        self.hexes = hexmodel
        self.color = color
        self.pos = pos
        self.direction = helpfunc.rand_dir() if direction is None else direction

    def draw_bullet(self):
        self.hexes.set_cell(self.pos, hue_to_color(self.color))

    def move_bullet(self):
        new_spot = helpfunc.hex_in_direction(self.pos, self.direction, 1)  # Where is the bullet going?
        if self.hexes.cell_exists(new_spot):	 # Is new spot off the board?
            self.pos = new_spot  # On board. Update spot
            self.draw_bullet()
            return True
        else:
            return False  # Off board. Kill.


class Trail(object):
    def __init__(self, hexmodel, color, intense, pos):
        self.hexes = hexmodel
        self.pos = pos
        self.h = self.pos[0]
        self.color = color
        self.intense = intense

    def draw_trail(self):
        if self.hexes.cell_exists(self.pos):
            self.hexes.set_cell(self.pos, gradient_wheel(hue_to_color(self.color), self.intense))

    def fade_trail(self):
        self.intense -= 0.15
        return self.intense > 0


class Planet(object):
    def __init__(self, hexmodel, pos, center, color, direction):
        self.hexes = hexmodel
        self.pos = pos
        self.color = color
        self.direction = direction
        self.center = center
        self.trails = []  # List that holds trails
        self.life = randint(20, 300)

    def draw_planet(self):

        self.fade_trails()

        self.draw_add_trail(self.color, 1, self.pos)  # Draw the center

        # Draw an outer ring
        for cell in helpfunc.hex_ring(self.pos, 1):
            self.draw_add_trail(self.color, 1, cell)

    def move_planet(self):
        new_spot = helpfunc.clock_cell(self.pos, self.direction, self.center)
        if new_spot == self.pos:
            self.life = 0  # Kill stationary planets
            return
        self.pos = new_spot
        self.life -= 1
        if helpfunc.one_in(5):
            self.center = choice(helpfunc.hex_ring(self.center, 1))
        return self.life > 0

    def draw_add_trail(self, color, intense, pos):
        if self.hexes.cell_exists(pos):
            self.hexes.set_cell(pos, gradient_wheel(hue_to_color(color), intense))
            self.trails.append(Trail(self.hexes, color, intense, pos))

    def fade_trails(self):
        for trail in reversed(self.trails):	 # Plot last-in first
            trail.draw_trail()
            if not trail.fade_trail():
                self.trails.remove(trail)


class Planets(object):
    def __init__(self, hexmodel):
        self.name = "Planets"
        self.hexes = hexmodel
        self.planets = []  # List that holds Planet objects
        self.bullets = []  # List that holds Bullet objects
        self.speed = 1.0 / randint(2, 10)
        self.color = random_hue()

    def next_frame(self):

        self.planets = [Planet(hexmodel=self.hexes,
                               pos=choice(helpfunc.hex_ring(helpfunc.get_center(h), 5)),
                               center=(h, randint(-1,1), randint(-1,1)),
                               color=random_hue(), direction=helpfunc.plus_or_minus())
                        for h in helpfunc.all_hexes()]

        while True:

            if len(self.planets) < (NUM_HEXES * 2) and helpfunc.one_in(20):
                h = helpfunc.get_random_hex()
                self.planets.append(Planet(hexmodel=self.hexes,
                                    pos=choice(helpfunc.hex_ring(helpfunc.get_center(h), 5)),
                                    center=(h, randint(-1,1), randint(-1,1)),
                                    color=random_hue(), direction=helpfunc.plus_or_minus()))

            self.hexes.black_all_cells()

            # Draw the Planets
            for planet in self.planets:
                planet.draw_planet()

                if not planet.move_planet():
                    for direction in helpfunc.all_dir():  # Cause explosion of bullets
                        bullet_color = (255 + planet.color + randint(-15, 15)) % 255
                        self.bullets.append(Bullet(hexmodel=self.hexes, color=bullet_color, pos=planet.pos,
                                                   direction=direction))

                    self.planets.remove(planet)	# Kill Planet

            # Draw the Bullets
            for bullet in self.bullets:
                bullet.draw_bullet()
                if not bullet.move_bullet():
                    self.bullets.remove(bullet)

            self.color = (self.color + 1) % 255  # Change the colors

            yield self.speed
