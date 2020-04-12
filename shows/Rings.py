from random import random, randint, choice
from color import random_hue, hue_to_color, random_color, black, change_color, random_color_range, gradient_wheel

import HelperFunctions as helpfunc


class Ring(object):
    def __init__(self, hexmodel, main_color, pos=None):
        self.hexes = hexmodel
        self.color = random_color_range(main_color, 0.2)
        self.pos = self.hexes.rand_cell() if not pos else pos
        self.size = randint(5, 9)	# Random ring size
        self.direction = helpfunc.rand_dir()
        self.life = randint(50, 200)	# how long a ring is around

    def decrease_life(self):
        self.life -= 1
        return self.life > 0

    def draw_ring(self):
        intensity = reversed([0.2, 0.4, 0.6, 0.8, 1.0])
        for (ring, grade) in zip(range(self.size-3, self.size+2), intensity):
            self.hexes.set_cells(helpfunc.hex_ring(self.pos, ring), gradient_wheel(self.color, grade))

    def move_ring(self):
        while True:
            new_spot = helpfunc.hex_in_direction(self.pos, self.direction, 1)  # Where is the ring going?
            h, x, y = new_spot
            if abs(x) < 7 and abs(y) < 7:
                self.pos = new_spot	# On board. Update spot
                break
            self.direction = helpfunc.rand_dir()  # Off board. Pick a new direction


class Rings(object):
    def __init__(self, hexmodel):
        self.name = "Rings"        
        self.hexes = hexmodel
        self.rings = []	 # List that holds Rings objects
        self.speed = 0.1
        self.main_color = random_color()

    def next_frame(self):

        self.rings = [Ring(self.hexes, self.main_color, helpfunc.get_center(h)) for h in helpfunc.all_hexes()]

        while True:

            # Check how many rings are in play
            # If no drops, add one. Otherwise if rings < 8, add more rings randomly
            if len(self.rings) < helpfunc.NUM_HEXES * 2 and helpfunc.one_in(25):
                self.rings.append(Ring(self.hexes, self.main_color))

            self.hexes.black_all_cells()

            # Draw all the rings
            # Increase the size of each drop - kill a drop if at full size
            for ring in self.rings:
                ring.draw_ring()
                ring.move_ring()
                if not ring.decrease_life():
                    self.rings.remove(ring)

            yield self.speed  	# random time set in init function
