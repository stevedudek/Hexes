from math import sin
from color import random_hue, hue_to_color, random_color, black, gradient_wheel, rgb_to_hsv
from random import random, randint, choice

import HelperFunctions as helpfunc


class Bullet(object):
    def __init__(self, hexmodel, pos, color, direction):
        self.hexes = hexmodel
        self.color = color
        self.direction = direction
        self.pos = pos
        self.intense = 1

    def draw_bullet(self):
        self.hexes.set_cell(self.pos, helpfunc.gradient_wheel(self.color, self.intense))

    def move_bullet(self):
        new_spot = helpfunc.hex_in_direction(self.pos, self.direction)  # Where is the bullet shooting?
        if self.hexes.cell_exists(new_spot):  # Is new spot off the board?
            self.pos = new_spot  # On board. Update spot
            self.intense -= 0.05
            return True  # Still traveling
        else:
            return False  # Off board - kill


class Sprocket(object):
    def __init__(self, hexmodel, center, color, min, thick):
        self.hexes = hexmodel
        self.color = color
        self.min = min
        self.thick = thick
        self.center = center
        self.life = randint(20, 100)
        self.blade = randint(5, 15) / 10.0
        self.color_churn = randint(2, 10)

    def draw_sprocket(self, clock):
        for r in range(self.min, self.min + self.thick):
            ring_cells = helpfunc.hex_ring(self.center, r)
            num_cells = len(ring_cells)
            for i in range(num_cells):
                col = (self.color + clock + (r * self.color_churn)) % 255
                attenuation = 1 - ( ((i + clock) % r) * (1.0 / (r * self.blade)))
                if attenuation < 0:
                    attenuation = 0
                if r % 2:
                    index = num_cells - i - 1
                else:
                    index = i
                if self.hexes.cell_exists(ring_cells[index]):
                    self.hexes.set_cell(ring_cells[index], gradient_wheel(hue_to_color(col), attenuation))

        if helpfunc.one_in(6):	# Flash the hole - Greg's suggestion
            col = (self.color + clock) % 255
            self.hexes.set_cell(self.center, hue_to_color(col)) # center

            for r in range(self.min):
                ring_cells = helpfunc.hex_ring(self.center, r)
                col = (self.color + clock + (r * self.color_churn)) % 255
                self.hexes.set_cells(ring_cells, hue_to_color(col))

    def move_sprocket(self):
        self.life -= 1
        return self.life > 0


class Sprockets(object):
    def __init__(self, hexmodel):
        self.name = "Sprockets"
        self.hexes = hexmodel
        self.sprockets = []  # List that holds Sprockets objects
        self.bullets = []  # List that holds Bullet objects
        self.direction = 1
        self.clock = 1000
        self.speed = 0.2 * randint(1, 4)

    def next_frame(self):

        while True:

            if len(self.sprockets) < helpfunc.NUM_HEXES:
                for h in helpfunc.all_hexes():
                    self.sprockets.append(Sprocket(self.hexes, center=helpfunc.get_center(h), color=random_hue(),
                                                   min=randint(1, 4), thick=7))

            self.hexes.black_all_cells()

            # Draw the Sprockets

            for sprocket in self.sprockets:
                sprocket.draw_sprocket(self.clock)
                if not sprocket.move_sprocket:
                    self.sprockets.remove(sprocket)

            # Draw the Bullets

            for bullet in self.bullets:
                bullet.draw_bullet()
                if not bullet.move_bullet():
                    self.bullets.remove(bullet)

            yield self.speed  	# random time set in init function

            self.clock += self.direction

            if helpfunc.one_in(50):
                self.direction *= -1