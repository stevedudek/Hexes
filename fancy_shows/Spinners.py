from color import gradient_wheel, random_color, change_color
from random import random, choice

import HelperFunctions as helpfunc


class Bullet(object):
    def __init__(self, hexmodel, color, pos):
        self.hexes = hexmodel
        self.color = color
        self.pos = pos
        self.direction = helpfunc.rand_dir()

    def draw_bullet(self):
        self.hexes.set_cell(self.pos, self.color)

    def move_bullet(self):
        new_spot = helpfunc.hex_in_direction(self.pos, self.direction, 1)  # Where is the bullet going?
        if self.hexes.cell_exists(new_spot):	 # Is new spot off the board?
            self.pos = new_spot	# On board. Update spot
            self.draw_bullet()
            return True
        else:
            return False  # Off board. Kill.


class Spinners(object):
    def __init__(self, hexmodel):
        self.name = "Spinners"
        self.hexes = hexmodel
        self.bullets = []  # List that holds Bullets objects
        self.speed = random() + 0.05
        self.background = random_color()  # Background color
        self.spincolor = random_color()  # Spinner color
        self.center = helpfunc.get_center(helpfunc.get_random_hex())
        self.time = 0

    def next_frame(self):

        while True:

            # Randomly fire a bullet
            for h in helpfunc.all_hexes():
                spin_center = (h, 4, 0)
                self.bullets.append(Bullet(hexmodel=self.hexes, color=self.spincolor,
                                           pos=choice(self.mirror_hexes(spin_center))))
                self.draw_background()
                self.draw_spinners(spin_center)

                # Draw the bullets
                for bullet in self.bullets:
                    if not bullet.move_bullet():	# bullet has moved off the board
                        self.bullets.remove(bullet)	# kill the bullet

                self.time += 1

                # Random move the spin centers

                if helpfunc.one_in(10):
                    new_spot = choice(helpfunc.hex_ring(spin_center, 1))
                    if self.hexes.cell_exists(choice(helpfunc.hex_ring(spin_center, 1))):
                        spin_center = new_spot

            # Change the colors
            self.background = change_color(self.background, 0.05)
            self.spincolor = change_color(self.background, -0.1)

            yield self.speed  	# random time set in init function

    def draw_background(self):
        """Draw the background - concentric rings of decreasing intensities"""
        for i in range(6):  # total number of rings
            self.hexes.set_cells(helpfunc.hex_ring(self.center, i),
                                 gradient_wheel(self.background, 1 - (i / 8.0)))

        # Draw the center of the rings
        self.hexes.set_cell(self.center, gradient_wheel(self.background, 1))

    def draw_spinners(self, spin_center):
        """Draw the spinners"""
        self.draw_mirrored(spin_center, gradient_wheel(self.spincolor, 1))

        for ring_size in [5, 10, 15]:
            for ring in range(ring_size):
                ring_coords = helpfunc.hex_ring(spin_center, 1)
                coord = ring_coords[ring_size % len(ring_coords)]
                if self.hexes.cell_exists(coord):
                    gradient = 1 - (abs(ring_size - (self.time % ring_size)) / float(ring_size - 1))
                    self.draw_mirrored(coord, gradient_wheel(self.spincolor, gradient))

    def draw_mirrored(self, coord, color):
        """Draw six mirrored hexes"""
        if self.hexes.cell_exists(coord):
            self.hexes.set_cell(color, coord)  # Draw the initial hex

            # Rotate five times and keep drawing
            for coord in self.mirror_hexes(coord):
                self.hexes.set_cell(coord, color)

    def mirror_hexes(self, coord):
        """Find the five other mirrored hexes for a given hex"""
        coords = [coord]
        for i in range(5):
            coord = self.rotate_left(coord)
            coords.append(coord)
        return coords

    @staticmethod
    def rotate_left(coord):
        (p, q, r) = coord
        (x, y, z) = (q, r, -q-r)  # Convert to cube coordinates
        (left_x, left_y, left_z) = (-z, -x, -y)
        return (p, left_x, left_y)  # Convert back to axial coordinates