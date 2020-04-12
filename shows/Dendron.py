from random import random, randint, choice
from color import random_hue, hue_to_color, random_color, black, change_color, random_color_range, gradient_wheel

import HelperFunctions as helpfunc


class Dendron(object):
    def __init__(self, hexmodel, color, pos, direction, life):
        self.hexes = hexmodel
        self.color = color
        self.pos = pos
        self.direction = direction
        self.life = life  # How long the branch has been around

    def draw_dendron(self, inversion):
        ratio = self.life / 10.0 if inversion else 1 - self.life / 40.0  # light center

        self.hexes.set_cells(helpfunc.mirror_hexes(self.pos), gradient_wheel(self.color, ratio))

        if helpfunc.one_in(4):
            self.direction = helpfunc.turn_left_or_right(self.direction)

    def move_dendron(self):
        new_spot = helpfunc.hex_in_direction(self.pos, self.direction)  # Where is the dendron going?
        if self.hexes.cell_exists(new_spot):  # Is new spot off the board?
            self.pos = new_spot  # On board. Update spot
            self.life += 1
            return True
        return False  # Off board. Kill.


class Dendrons(object):
    def __init__(self, hexmodel):
        self.name = "Dendrons"
        self.hexes = hexmodel
        self.live_dendrons = []  # List that holds Dendron objects
        self.speed = 0.02
        self.main_color = random_color()  # Main color of the show
        self.inversion = randint(0,1)  # Toggle for effects

    def next_frame(self):

        self.live_dendrons = [Dendron(hexmodel=self.hexes, color=self.main_color, pos=helpfunc.get_center(h),
                                      direction=5, life=0) for h in helpfunc.all_hexes()]

        while True:

            # Randomly add a center dendron

            if helpfunc.one_in(5):
                self.live_dendrons.append(Dendron(hexmodel=self.hexes, color=self.main_color,
                                                  pos=helpfunc.get_random_center(), direction=5, life=0))

            for dendron in self.live_dendrons:
                dendron.draw_dendron(self.inversion)

                if helpfunc.one_in(20):
                    new_dir = helpfunc.turn_left_or_right(dendron.direction)
                    self.live_dendrons.append(Dendron(hexmodel=self.hexes, color=dendron.color,
                                                      pos=dendron.pos, direction=new_dir, life=dendron.life))

                if not dendron.move_dendron():  # dendron has moved off the board
                    self.live_dendrons.remove(dendron)  # kill the dendron

            if helpfunc.one_in(10):
                self.main_color = random_color_range(self.main_color, 0.05)

            yield self.speed
