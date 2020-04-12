from color import gradient_wheel, random_color, random_color_range
from HelperFunctions import rand_dir, hex_ring, hex_in_direction, one_in, get_random_hex, get_center, \
    turn_left_or_right
from hex import NUM_HEXES
from random import random, randint, choice


class Branch(object):
    def __init__(self, hexmodel, position, color, direction, life):
        self.hexes = hexmodel
        self.pos = position
        self.color = random_color_range(color, shift_range=0.1)
        self.direction = direction
        self.life = life  # How long the branch has been around

    def draw_branch(self):
        self.hexes.set_cell(self.pos, gradient_wheel(self.color, 1.0 - (self.life / 20.0)))

    def move_branch(self):
        new_spot = hex_in_direction(self.pos, self.direction)  # Where is the branch going?
        if self.hexes.cell_exists(new_spot):  # Is new spot off the board?
            self.pos = new_spot	 # On board. Update spot
            self.life += 1
            return True
        return False  # Off board. Pick a new direction


class Branches(object):
    def __init__(self, hexmodel):
        self.name = "Branches"
        self.hexes = hexmodel
        self.live_branches = []	# List that holds Branch objects
        self.main_color = random_color()
        self.main_dir = rand_dir()
        self.speed = 0.1

    def next_frame(self):

        while True:

            # Check how many branches are in play
            if len(self.live_branches) < NUM_HEXES or one_in(5):
                self.live_branches.append(Branch(hexmodel=self.hexes,
                                                 position=choice(hex_ring(get_center(get_random_hex()), 5)),
                                                 color = self.main_color,
                                                 direction=self.main_dir,
                                                 life=0))

            for branch in self.live_branches:
                branch.draw_branch()

                # Chance for branching
                if one_in(5):  # Create a fork
                    self.live_branches.append(Branch(hexmodel=self.hexes,
                                                     position=branch.pos,
                                                     color= branch.color,
                                                     direction=turn_left_or_right(branch.direction),
                                                     life=branch.life))

                if not branch.move_branch():  # branch has moved off the board
                    self.live_branches.remove(branch)  # kill the branch

            # Infrequently change the dominate direction
            if one_in(100):
                self.main_dir = turn_left_or_right(self.main_dir)

            yield self.speed