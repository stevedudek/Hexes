from random import randint
from HelperFunctions import one_in, rand_dir, hex_ring, hex_in_direction
from color import random_color, random_color_range, gradient_wheel


class Ball(object):
    def __init__(self, hexmodel, maincolor):
        self.hexes = hexmodel
        self.color = random_color_range(maincolor, 30)
        self.pos = self.hexes.rand_cell()
        self.size = randint(2, 5)
        self.dir = rand_dir()
        self.life = randint(50, 200)  # how long a ball is around

    def decrease_life(self):
        self.life -= 1
        return self.life

    def draw_ball(self):
        self.hexes.set_cell(self.pos, self.color)  # Draw the center
        for i in range(self.size):
            for coord in hex_ring(self.pos, i):
                self.hexes.set_cell(coord, gradient_wheel(self.color, 1 - (0.2 * (i + 1))))

    def move_ball(self):
        while True:
            new_spot = hex_in_direction(self.pos, self.dir)  # Where is the ball going?
            if self.hexes.cell_exists(new_spot):  # Is new spot off the board?
                self.pos = new_spot  # On board. Update spot
                break
            self.dir = rand_dir()  # Off board. Pick a new direction


class Balls(object):
    def __init__(self, hexmodel):
        self.name = "Balls"
        self.hexes = hexmodel
        self.balls = []	 # List that holds Balls objects
        self.speed = 1.0 / randint(1, 10)
        self.maincolor = random_color()  # Main color of the show

    def next_frame(self):

        while True:

            # Check how many balls are in play
            if not self.balls or (len(self.balls) < 3 and one_in(25)):
                self.balls.append(Ball(self.hexes, self.maincolor))

            self.hexes.black_all_cells()

            # Draw all the balls
            # Increase the size of each drop - kill a drop if at full size
            for b in self.balls:
                b.draw_ball()
                b.move_ball()
                if not b.decrease_life():
                    self.balls.remove(b)

            yield self.speed

