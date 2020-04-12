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

    def draw_branch(self, inversion):
        ratio = self.life / 10.0 if inversion else 1 - self.life / 40.0
        self.hexes.set_cell(self.pos, gradient_wheel(self.color, ratio))

        if one_in(4):
            self.direction = turn_left_or_right(self.direction)

    def move_branch(self):
        new_spot = hex_in_direction(self.pos, self.direction)  # Where is the branch going?
        if self.hexes.cell_exists(new_spot):  # Is new spot off the board?
            self.pos = new_spot	 # On board. Update spot
            self.life += 1
            return True
        return False  # Off board. Pick a new direction


class CenterBranches(object):
    def __init__(self, hexmodel):
        self.name = "Center Branches"
        self.hexes = hexmodel
        self.live_branches = []	# List that holds Branch objects
        self.main_color = random_color()
        self.main_dir = rand_dir()
        self.inversion = randint(0, 1)  # Toggle for effects
        self.speed = 0.05

    def next_frame(self):

        while True:

            for h in range(NUM_HEXES):
                self.live_branches.append(Branch(hexmodel=self.hexes,
                                                 position=(get_center(h)),
                                                 color=self.main_color,
                                                 direction=rand_dir(),
                                                 life=0))

            for branch in self.live_branches:
                branch.draw_branch(self.inversion)

                # Chance for branching
                if one_in(20):  # Create a fork
                    self.live_branches.append(Branch(hexmodel=self.hexes,
                                                     position=branch.pos,
                                                     color=branch.color,
                                                     direction=turn_left_or_right(branch.direction),
                                                     life=branch.life))

                if not branch.move_branch():  # branch has moved off the board
                    self.live_branches.remove(branch)  # kill the branch

            # Randomly change the main color
            if one_in(10):
                self.main_color = random_color_range(self.main_color, 0.2)

            yield self.speed  # random time set in init function



# class CenterBranches(object):
# 	def __init__(self, hexmodel):
# 		self.name = "Center Branches"
# 		self.hexes = hexmodel
# 		self.livebranches = []	# List that holds Branch objects
# 		self.speed = 0.05
# 		self.maincolor =  randint(0,255)	# Main color of the show
# 		self.inversion = randint(0,1)	# Toggle for effects
#
# 	def next_frame(self):
#
# 		while (True):
#
# 			# Add a center branch
#
# 			newbranch = Branch(self.hexes,
# 					self.maincolor, 	# color
# 					(0,0), 				# center
# 					randint(0,5), 		# Random initial direction
# 					0)					# Life = 0 (new branch)
# 			self.livebranches.append(newbranch)
#
# 			for b in self.livebranches:
# 				b.draw_branch(self.inversion)
#
# 				# Chance for branching
# 				if randint(0,20) == 1:	# Create a fork
# 					if randint(0,1) == 1:
# 						newdir = (5 + b.dir - 1) % 5 # fork left
# 					else:
# 						newdir = (b.dir + 1) % 5 # fork right
# 					newbranch = Branch(self.hexes, b.color, b.pos, newdir, b.life)
# 					self.livebranches.append(newbranch)
#
# 				if b.move_branch() == False:	# branch has moved off the board
# 					self.livebranches.remove(b)	# kill the branch
#
# 			self.hexes.go()
#
# 			# Randomly change the main color
# 			if randint(0,10) == 1:
# 				self.maincolor = (255 + randint(-10,10) + self.maincolor) % 255
#
#
# 			yield self.speed  	# random time set in init function