from color import rgb_to_hsv, black
from random import random, choice, randint, shuffle

import HelperFunctions as helpfunc


class Branch(object):
    def __init__(self, hexmodel, pos, direction, life):
        self.hexes = hexmodel
        self.pos = pos
        self.direction = direction
        self.life = life  # How long the branch has been around

    def move_branch(self):
        # Random chance that path changes
        if helpfunc.one_in(6):
            self.direction = helpfunc.turn_left_or_right(self.direction)

        self.pos = helpfunc.hex_in_direction(self.pos, self.direction)  # Where is the dendron going?
        if self.life > 0:
            self.life -= 1
        return self.pos

    def is_branch_dead(self):
        return self.life <= 0


class Leaf(object):
    def __init__(self, hexmodel, pos, color):
        self.hexes = hexmodel
        self.pos = pos
        self.color = color
        self.falling = False

    def draw_leaf(self):
        self.hexes.set_cell(self.pos, self.color)

    def turn_red(self):
        r, g, b = self.color
        self.color = rgb_to_hsv((255, g, 0))

    def fall(self):
        self.falling = True

    def move_leaf(self):
        if self.falling:
            direction = randint(4, 6) % 6
            self.pos = helpfunc.hex_in_direction(self.pos, direction)
            return self.hexes.cell_exists(self.pos)


class Seasons(object):
    def __init__(self, hexmodel):
        self.name = "Seasons"
        self.hexes = hexmodel
        self.treespot = []  # List that holds branch cells
        self.leaves = []  # List that holds leaf objects
        self.sky_color = black()  # Set for each season
        self.ground_color = black()  # Set for each season
        self.treecolor = rgb_to_hsv((54, 0, 0))  # Dark brown

    def next_frame(self):

        self.fill_branches()  # Figure out the position of the tree branches

        while True:

            # Spring

            self.sky_color = rgb_to_hsv((100, 100, 255))
            self.ground_color = rgb_to_hsv((154, 150, 100))

            self.draw_ground(self.sky_color, self.ground_color)
            self.draw_tree()
            yield 5

            self.sky_color = rgb_to_hsv((50, 50, 255))
            self.ground_color = rgb_to_hsv((54, 255, 50))
            self.draw_ground(self.sky_color, self.ground_color)
            self.draw_tree()
            yield 0.1

            shuffle(self.treespot)
            for cell in self.treespot:
                if self.hexes.cell_exists(cell):
                    self.hexes.set_cell(cell, rgb_to_hsv((255,230,230)))
                    yield 0.2

            shuffle(self.treespot)
            for cell in self.treespot:
                if self.hexes.cell_exists(cell):
                    self.hexes.set_cell(cell, rgb_to_hsv((0,255,0)))
                    yield 0.2

            # Big leaves

            shuffle(self.treespot)

            for cell in self.treespot:
                green = rgb_to_hsv((0, randint(50, 255), 0))

                self.leaves.append(Leaf(self.hexes, cell, green))

                for cell in helpfunc.hex_ring(cell, 1):
                    self.leaves.append(Leaf(self.hexes, cell, green))

                self.draw_leaves()
                yield 0.5

            # Apples

            apple_color = rgb_to_hsv((255, 0, 0))
            for i in range(5):
                apple = choice(self.treespot)
                if self.hexes.cell_exists(apple):
                    self.hexes.set_cell(apple, apple_color)
                yield 0.5

            yield 5

            # Fall foliage

            shuffle(self.leaves)

            for leaf in self.leaves:
                leaf.turn_red()

                self.draw_leaves()
                yield 0.05

            # Drop leaves

            self.sky_color = rgb_to_hsv((0, 0, 200))
            self.ground_color = rgb_to_hsv((54, 155, 50))

            shuffle(self.leaves)

            for leaf in self.leaves:
                leaf.fall()

                for leaf2 in self.leaves:
                    leaf2.move_leaf()

                self.draw_ground(self.sky_color, self.ground_color)
                self.draw_tree()
                self.draw_leaves()
                yield 0.1

            self.sky_color = rgb_to_hsv((0, 0, 100))
            self.ground_color = rgb_to_hsv((25, 105, 25))

            for _ in range(10):
                for l2 in self.leaves:
                    l2.move_leaf()

                self.draw_ground(self.sky_color, self.ground_color)
                self.draw_tree()
                self.draw_leaves()
                yield 0.1

            self.sky_color = rgb_to_hsv((0, 0, 50))
            self.ground_color = rgb_to_hsv((25, 50, 25))

            # Remove leaves

            for leaf in self.leaves:
                self.leaves.remove(leaf)
                self.draw_ground(self.sky_color, self.ground_color)
                self.draw_tree()
                self.draw_leaves()
                yield 0.1

            yield 5

            # Destroy tree

            self.branches = []
            self.hexes.black_all_cells()
            yield 4

    def draw_leaves(self):
        for leaf in self.leaves:
            leaf.draw_leaf()

    def bloom_tree(self, tree_cells, color):
        shuffle(tree_cells)
        for cell in tree_cells:
            if self.hexes.cell_exists(cell):
                self.hexes.set_cell(cell, color)
                yield 0.5

    def draw_ground(self, sky, ground):
        self.hexes.set_all_cells(sky)
        for h in helpfunc.all_hexes():
            self.hexes.set_cells(helpfunc.get_box((h, -2, 10), 10, 6), ground)

    def draw_tree(self):
        for h in helpfunc.all_hexes():
            self.hexes.set_cells(helpfunc.get_box((h, -1, 1), 3, 3, False), self.treecolor)  # Trunk
        self.hexes.set_cells(self.treespot, self.treecolor)  # Branches

    def fill_branches(self):
        branches = []

        for h in helpfunc.all_hexes():
            branches += [Branch(self.hexes, (h, -1, 0), 3, 4),
                         Branch(self.hexes, (h, 0, 0), 2, 5),
                         Branch(self.hexes, (h, 1, -1), 1, 4)]

        for branch in branches:
            self.treespot.append(branch.move_branch())
            if branch.is_branch_dead():
                branches.remove(branch)
            else:
                if helpfunc.one_in(3):  # New branch
                    branches.append(Branch(self.hexes, pos=branch.pos,
                                           direction=(branch.direction + 6 + (randint(0, 2) - 1)) % 6,
                                           life=branch.life))