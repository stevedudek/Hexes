from color import gradient_wheel, random_color, change_color
from random import randint, choice, random

import HelperFunctions as helpfunc


class Spinner(object):
    def __init__(self, hexmodel, pos):
        self.hexes = hexmodel
        self.pos = pos
        self.expand = 0	 # -1: contracting, 0: nothing, 1: expanding
        self.size = 1

    def explode_spinner(self):
        self.expand = 1

    def is_resting(self):
        return self.expand == 0

    def draw_spinner(self, spincolor, explodecolor, time):
        color = spincolor #if self.expand == 0 else explodecolor
        self.hexes.set_cell(self.pos, color)  # Draw the center

        # Draw the spinning bits
        for ring_size in range(1, self.size + 1):
            ringcells = helpfunc.hex_ring(self.pos, ring_size)
            num = len(ringcells)
            for i, coord in enumerate(ringcells):
                gradient = 1 - (abs(i - (time % num)) / num)
                self.hexes.set_cell(coord, gradient_wheel(color, gradient))

    def move_spinner(self):
        newspot = choice(helpfunc.hex_ring(self.pos, 1))
        if self.hexes.cell_exists(newspot):
            self.pos = newspot

        self.expand += self.size
        if self.expand > 12:
            self.expand = -1  # Contract!
        if self.expand <= 1:
            self.expand = 0	 # Done


class ExplodingSpinners(object):
    def __init__(self, hexmodel):
        self.name = "Exploding spinners"
        self.hexes = hexmodel
        self.spinners = []	# List that holds Spinner objects
        self.speed = random() + 0.05
        self.explode_color = random_color()  # Color for exploding spinner
        self.spincolor = random_color()  # Spinner color
        self.time = 0

    def next_frame(self):

        self.set_up_spinners()

        while True:

            # Draw the spinners - draw exploding spinners last

            for s in self.spinners:
                s.draw_spinner(self.spincolor, self.explode_color, self.time)
                if not s.is_resting():
                    s.move_spinner()

            # Explode a spinner
            if self.all_resting() and helpfunc.one_in(5):
                choice(self.spinners).explode_spinner()

            # Change the colors
            self.explode_color = change_color(self.explode_color, 0.05)
            self.spincolor = change_color(self.spincolor, -0.01)

            self.time += 1

            yield self.speed  	# random time set in init function

    def all_resting(self):
        return all([spinner.is_resting() for spinner in self.spinners])

    def set_up_spinners(self):
        """Initialize the spinners"""
        self.spinners = [Spinner(self.hexes, helpfunc.get_center(h)) for h in helpfunc.all_hexes()]  # Center spinner

        # Dendron spinners
        for h in helpfunc.all_hexes():
            size = randint(3, 6)
            self.spinners += [Spinner(self.hexes, coord) for coord in self.mirror_hexes((h, size, 0))]

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
        (x, y, z) = (q, r, -q - r)  # Convert to cube coordinates
        (left_x, left_y, left_z) = (-z, -x, -y)
        return (p, left_x, left_y)  # Convert back to axial coordinates