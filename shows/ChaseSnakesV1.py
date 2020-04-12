"""
A Snake object is a chain of hexes of N-Length from head_color trailing to black=255, 255, 255. Snakes pick a random
direction to go and push their head color onto that random direction, while gradually dimming their body.
"""
# from webcolors import name_to_rgb
from color import rgb_to_hsv
import random

from HelperFunctions import neighbors, get_random_center


class Segment(object):
    def __init__(self, segment_color, hex_coord):
        self.segment_color = segment_color
        self.hex_coord = hex_coord


class Snake(object):
    def __init__(self, starting_cell=None, head_color=(255, 0, 255), snake_length=10):
        self.starting_cell = starting_cell if starting_cell is not None else get_random_center()
        self.head_color = head_color
        self.snake_length = snake_length
        self.hex_chain = [Segment(head_color, starting_cell)]

    def ___potential_heads(self, hexes):
        # Snakes may never fall off the map or double back on themselves.
        potential_heads = []
        if self.hex_chain[0].hex_coord is not None:
            for item in neighbors(self.hex_chain[0].hex_coord):
                if hexes.cell_exists(item):
                    if len(self.hex_chain) > 1:
                        if item != self.hex_chain[1].hex_coord:
                            potential_heads.append(item)
                    else:
                        potential_heads.append(item)

        return potential_heads

    # and item not in [segment.hex_coord for segment in self.hex_chain]]

    def ___trapped_snake(self, hexes):
        """
        A trapped snake is a snake where all neighbors of the head are in the body.

        Poor bugger curled in on himself and now he must die.
        """
        return not self.___potential_heads(hexes)

    def paint(self, hexes):
        for segment in reversed(self.hex_chain):
            hexes.set_cell(segment.hex_coord, rgb_to_hsv(segment.segment_color))

    def take_step(self, hexes):
        """
        Moves the snake forward one step that isn't occupied by itself

        1) If a snake has no where to go, it resets in the center.
        2) Each body segment dims towards darkness by one/snake_length step (
        1) Pushes a random head full intensity hex that isn't already in the hex_chain (a self collision)
        2) if length == snake_length, pop the tail off
        3) Each body segment dims towards darkness by one/snake_length step
        """

        if self.___trapped_snake(hexes):
            self.hex_chain = [Segment(self.head_color, self.starting_cell)]
        else:
            potential_heads = self.___potential_heads(hexes)

            for segment in self.hex_chain:
                new_red = segment.segment_color[0] + (255 - self.head_color[0]) / self.snake_length
                new_blue = segment.segment_color[1] + (255 - self.head_color[1]) / self.snake_length
                new_green = segment.segment_color[2] + (255 - self.head_color[2]) / self.snake_length
                segment.segment_color = (new_red, new_blue, new_green)

            self.hex_chain.insert(0, Segment(self.head_color, random.choice(potential_heads)))
            if len(self.hex_chain) > self.snake_length:
                self.hex_chain.pop()


def generateRandomColor(initial_color=None):
    new_red = random.randint(0, 256)
    new_green = random.randint(0, 256)
    new_blue = random.randint(0, 256)

    if initial_color is not None:
        new_red += initial_color[0] / 2
        new_green += new_green + initial_color[1] / 2
        new_blue += new_blue + initial_color[2] / 2

    return (new_red, new_green, new_blue)


class ChaseSnakesV1(object):
    def __init__(self, hexmodel):
        self.name = "ChaseSnakesV1"
        self.hexes = hexmodel
        self.max_snakes = 7
        # initialize some snakes!
        initial_color = (255, 0, 0)
        self.snake_list = [Snake(head_color=generateRandomColor(initial_color)) for x in range(0, self.max_snakes)]

    def next_frame(self):
        while True:
            self.hexes.set_all_cells([255, 255, 255])

            for snake in self.snake_list:
                snake.paint(self.hexes)
                snake.take_step(self.hexes)

            yield 0.2  # sleep time between frames
