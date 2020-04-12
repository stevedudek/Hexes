"""
A Snake object is a chain of hexes of N-Length from head_color trailing to black=255, 255, 255. Snakes pick a random
direction to go and push their head color onto that random direction, while gradually dimming their body. New improved
Snakes can have babies or can die.
"""
from color import rgb_to_hsv
import random

from HelperFunctions import neighbors, get_random_center

BABY_MAKER_CHANCE = 5  # 5 percent.
MAX_SNAKES = 8
INITIAL_SNAKE_LENGTH = 10
MIN_SNAKE_LENGTH = 5


class Segment(object):
    def __init__(self, segment_color, hex_coord):
        self.segment_color = segment_color
        self.hex_coord = hex_coord


class Snake(object):
    def __init__(self, starting_cell=get_random_center(), head_color=rgb_to_hsv((255, 0, 255)), snake_length=INITIAL_SNAKE_LENGTH):
        self.starting_cell = starting_cell
        self.head_color = head_color
        self.snake_length = snake_length
        self.max_pause = 5
        self.current_pause = 0
        self.snake_death = False
        self.hex_chain = [Segment(head_color, starting_cell)]

    def __eq__(self, other):
        return id(self) == id(other)

    def ___potential_heads(self, hexes, snake_list, ignore_collisions=False):
        # Snakes may never fall off the map, collide with themselves or collide with other snakes
        potential_heads = []
        occupied_hex_list = [segment.hex_coord for snake in snake_list for segment in snake.hex_chain]

        for potential_head in neighbors(self.hex_chain[0].hex_coord):
            if hexes.cell_exists(potential_head):
                if not ignore_collisions:
                    if potential_head not in occupied_hex_list:
                        potential_heads.append(potential_head)
                else:
                    potential_heads.append(potential_head)

        return potential_heads


    # and item not in [segment.hex_coord for segment in self.hex_chain]]

    def ___trapped_snake(self, hexes, snake_list):
        return not self.___potential_heads(hexes, snake_list)

    def paint(self, hexes):
        for segment in reversed(self.hex_chain):
            hexes.set_cell(segment.hex_coord, segment.segment_color)

    def take_step(self, hexes, snake_list):
        """
        Moves the snake forward one step that isn't occupied by itself

        1) If a snake has no where to go, it waits a turn and tries again. If it fails to move max_retry times, it
            just gives up and collides
        2) Each body segment dims towards darkness by one/snake_length step
        1) Pushes a random head full intensity hex that isn't already in another snakes hex_chain
        2) if length == snake_length, pop the tail off
        3) Each body segment dims towards darkness by one/snake_length step
        """
        new_snake = None
        if not self.snake_death:
            if self.___trapped_snake(hexes, snake_list):
                self.current_pause += 1
                if self.current_pause < self.max_pause:
                    return

                self.current_pause = 0
                potential_heads = self.___potential_heads(hexes, snake_list, ignore_collisions=True)
            else:
                potential_heads = self.___potential_heads(hexes, snake_list)

            if random.randint(0, 100) <= BABY_MAKER_CHANCE:
                if self.snake_length == MIN_SNAKE_LENGTH:
                    self.snake_death = True
                else:
                    self.snake_length -= 1
                    if len(snake_list) < MAX_SNAKES:
                        new_snake = Snake(starting_cell=random.choice(potential_heads),
                                          head_color=pick_new_color(self.head_color))

        for segment in self.hex_chain:
            new_red = segment.segment_color[0] + (255 - self.head_color[0]) / self.snake_length
            new_blue = segment.segment_color[1] + (255 - self.head_color[1]) / self.snake_length
            new_green = segment.segment_color[2] + (255 - self.head_color[2]) / self.snake_length
            segment.segment_color = (new_red, new_blue, new_green)

        if not self.snake_death:
            self.hex_chain.insert(0, Segment(self.head_color, random.choice(potential_heads)))

        if len(self.hex_chain) > self.snake_length or self.snake_death:
            self.hex_chain.pop()
            if not self.hex_chain:
                snake_list.remove(self)

        return new_snake


def pick_new_color(initial_color=None, minimum_intensity=100):
    new_red = random.randint(0, 256)
    new_green = random.randint(0, 256)
    new_blue = random.randint(0, 256)
    minimum_intensity_not_reached = True
    while minimum_intensity_not_reached:
        if initial_color is not None:
            new_red += initial_color[0] / 2
            new_green += initial_color[1] / 2
            new_blue += initial_color[2] / 2

        if new_red > minimum_intensity or new_blue > minimum_intensity or new_green > minimum_intensity:
            minimum_intensity_not_reached = False
            new_red = random.randint(0, 256)
            new_green = random.randint(0, 256)
            new_blue = random.randint(0, 256)

    return new_red, new_green, new_blue


class ChaseSnakesV2(object):
    def __init__(self, hexmodel):
        self.name = "ChaseSnakesV2"
        self.hexes = hexmodel
        self.initial_color = rgb_to_hsv((255, 0, 0))
        self.snake_list = [Snake(head_color=self.initial_color)]

    def next_frame(self):
        while True:
            self.hexes.set_all_cells((255, 255, 255))

            for snake in self.snake_list:
                snake.paint(self.hexes)
                new_snake = snake.take_step(self.hexes, self.snake_list)
                if new_snake is not None:
                    new_snake.paint(self.hexes)
                    self.snake_list.insert(0, new_snake)

            if len(self.snake_list) < 2:
                self.snake_list = [Snake(head_color=self.initial_color)]

            yield 0.2  # sleep time between frames
