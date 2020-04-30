from color import gradient_wheel, random_color, change_color, hue_to_color, random_hue, random_color_range
from random import random, choice, randint

import HelperFunctions as helpfunc


class Swirl(object):
    def __init__(self, hexmodel, color, pos, direction, sym, life):
        self.hexes = hexmodel
        self.color = color
        self.pos = pos
        self.direction = direction
        self.sym = sym  # 0, 1, 2, 3 = 1x, 2x, 3x, 6x symmetric
        self.life = life	# How long the branch has been around

    def draw_swirl(self):
        self.hexes.set_cells(self.multi_mirror_hexes(self.pos, self.sym),
                             gradient_wheel(self.color, 1 - self.life / 50.0))

        # Random chance that path changes - spirals only in one direction
        if helpfunc.one_in(2):
            self.direction = helpfunc.turn_right(self.direction)

    def move_swirl(self):
        new_spot = helpfunc.hex_in_direction(self.pos, self.direction)  # Where is the swirl going?
        if self.hexes.cell_exists(new_spot):  # Is new spot off the board?
            self.pos = new_spot	# On board. Update spot
            self.life += 1
            return self.life < 50
        return False	# Off board. Kill.

    @staticmethod
    def multi_mirror_hexes(coord, sym):
        """Find the other mirrored hexes for a given hex
           0 = no mirroring, 1 = 180-mirror, 2 = 120-mirror, 3 = 60-mirror"""
        if sym == 0:
            return [coord]

        coords = helpfunc.mirror_hexes(coord)
        if sym == 3:
            return coords
        elif sym == 2:
            return [coords[0], coords[2], coords[4]]
        elif sym == 1:
            return [coords[0], coords[3]]
        else:
            return []


class Swirls(object):
    def __init__(self, hexmodel):
        self.name = "Swirls"
        self.hexes = hexmodel
        self.live_swirls = []	# List that holds Swirl objects
        self.speed = 1.0 / randint(3, 15)
        self.main_color = random_color()

    def next_frame(self):

        self.live_swirls = [Swirl(hexmodel=self.hexes, color=self.main_color, pos=helpfunc.get_center(h),
                                  direction=randint(0,5), sym=randint(0,3), life=0)
                            for h in helpfunc.all_hexes()]

        while True:

            # Randomly add a center swirl

            if helpfunc.one_in(8):
                self.live_swirls.append(Swirl(hexmodel=self.hexes, color=self.main_color,
                                              pos=helpfunc.get_random_center(), direction=randint(0,5),
                                              sym=randint(0,3), life=0))
                self.main_color = random_color_range(self.main_color, 0.075)

            for swirl in self.live_swirls:
                swirl.draw_swirl()

                # Chance for branching
                if helpfunc.one_in(10):	# Create a fork
                    self.live_swirls.append(Swirl(hexmodel=self.hexes, color=swirl.color, pos=swirl.pos,
                                                  direction=helpfunc.turn_right(swirl.direction),
                                                  sym=swirl.sym, life=swirl.life))

                if not swirl.move_swirl():  # Swirl has moved off the board
                    self.live_swirls.remove(swirl)	# kill the branch

            yield self.speed
