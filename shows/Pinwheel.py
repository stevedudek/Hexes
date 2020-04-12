from random import randint
from color import change_color, gradient_wheel, random_color, random_color_range
import HelperFunctions as helpfunc


class Pinwheel(object):
    def __init__(self, hexmodel, color, pos, direction, life):
        self.hexes = hexmodel
        self.color = color
        self.pos = pos
        self.direction = direction
        self.life = life  # How long the branch has been around

    def draw_pinwheel(self):
        self.hexes.set_cells(self.three_mirror_hexes(self.pos), gradient_wheel(self.color, 1 - self.life / 20.0))

        # Random chance that path changes - spirals only in one direction
        if helpfunc.one_in(2):
            self.direction = helpfunc.turn_left(self.direction)

    def move_pinwheel(self):
        new_spot = helpfunc.hex_in_direction(self.pos, self.direction)  # Where is the pinwheel going?
        if self.hexes.cell_exists(new_spot):  # Is new spot off the board?
            self.pos = new_spot  # On board. Update spot
            self.life += 1
            return self.life < 20
        return False  # Off board. Kill.

    def three_mirror_hexes(self, coord):
        """Find the two other mirrored hexes (120-rotation) for a given hex"""
        return [helpfunc.mirror_hexes(coord)[index] for index in [1, 3, 5]]


class Pinwheels(object):
    def __init__(self, hexmodel):
        self.name = "Pinwheel"
        self.hexes = hexmodel
        self.live_pinwheels = []  # List that holds Pinwheel objects
        self.speed = 1.0 / randint(2, 20)
        self.maincolor = random_color()

    def next_frame(self):

        self.live_pinwheels = [Pinwheel(hexmodel=self.hexes, color=self.maincolor,
                                        pos=(h, randint(0, 6), 0), direction=5, life=0)
                               for h in helpfunc.all_hexes()]

        while True:

            # Randomly add pinwheel

            if len(self.live_pinwheels) < helpfunc.NUM_HEXES or helpfunc.one_in(8):
                self.live_pinwheels.append(Pinwheel(self.hexes, color=self.maincolor,
                                                    pos=(helpfunc.get_random_hex(), randint(0, 6), 0),
                                                    direction=5, life=0))

            for pinwheel in self.live_pinwheels:
                pinwheel.draw_pinwheel()

                if helpfunc.one_in(10):  # Create a fork
                    self.live_pinwheels.append(Pinwheel(hexmodel=self.hexes, color=pinwheel.color, pos=pinwheel.pos,
                                                        direction=helpfunc.turn_left(pinwheel.direction),
                                                        life=pinwheel.life))

                if not pinwheel.move_pinwheel():  # pinwheel has moved off the board
                    self.live_pinwheels.remove(pinwheel)  # kill the branch

            # Randomly change the main color
            if helpfunc.one_in(10):
                self.maincolor = random_color_range(self.maincolor, 0.05)

            yield self.speed  	# random time set in init function