from color import gradient_wheel, random_color, change_color, hue_to_color, random_hue, random_color_range
from random import random, choice, randint

import HelperFunctions as helpfunc

def create_snake_model(hexmodel):
    return SnakeModel(hexmodel)


class SnakeModel(object):
    def __init__(self, hexmodel):
        # similar to the Hex Model
        # this model contains a dictionary of hex coordinates
        # coordinates are the keys
        # the values are the presence of a snake:
        # 0 = no snake; number = snake ID

        # Transfer regular hexmodel to the snakemmap
        # And clear (set to 0) all of the snake hexes
        self.hexes = hexmodel
        self.snakemap = {coord: 0 for coord in self.hexes.cellmap.keys()}	# Dictionary of snake hexes

    def get_snake_value(self, coord, default=None):
        """Returns the snake value for a coordinate. Return 'default' if not found"""
        return self.snakemap.get(coord, default)

    def put_snake_value(self, coord, snakeID):
        """Puts the snakeID in the snake hex"""
        self.snakemap[coord] = snakeID

    def is_open_hex(self, coord):
        """"Returns True if the hex is open. Also makes sure hex is on the board"""
        return self.hexes.cell_exists(coord) and self.get_snake_value(coord) == 0

    def get_valid_directions(self, coord):
        """Get the valid / open direction a snake can move"""
        return [direction for direction in helpfunc.all_dir()
                if self.is_open_hex(helpfunc.hex_in_direction(coord, direction))]

    def pick_open_hex(self):
        """Pick a neighboring open hex"""
        open_hexes = [coord for coord in self.snakemap.keys() if self.is_open_hex(coord)]
        return choice(open_hexes) if open_hexes else None

    def remove_snake_path(self, snakeID):
        """In the snake map, changes all hexes with snakeID back to 0. Kills the particular snake path"""
        for coord in self.snakemap.keys():
            if self.get_snake_value(coord) == snakeID:
                self.put_snake_value(coord, 0)
                ## Activate the line below for quite a different effect
                #self.hexes.set_cell([0,0,0], coord) # Turn path back to black


class Snake(object):
    def __init__(self, hexmodel, main_color, snakeID, start_pos):
        self.hexes = hexmodel
        self.color = main_color
        self.snakeID = snakeID  # Numeric ID
        self.pos = start_pos  # Starting position
        self.direction = helpfunc.rand_dir()
        self.pathlength = 0
        self.alive = True

    def draw_snake(self):
        self.hexes.set_cell(self.pos, gradient_wheel(self.color, 1.0 - (self.pathlength / 50.0)))
        self.pathlength += 1


class Snakes(object):
    def __init__(self, hexmodel):
        self.name = "Snakes"
        self.hexes = hexmodel
        self.snakemap = create_snake_model(hexmodel)
        self.next_snake_id = 0
        self.live_snakes = {}	# Dictionary that holds Snake objects. Key is snakeID.
        self.speed = 0.1
        self.main_color = random_color()

    def next_frame(self):

        while True:

            # Check how many snakes are in play
            # If no snakes, add one. Otherwise if snakes < 4, add more snakes randomly
            if not self.live_snakes or helpfunc.one_in(10):
                start_pos = self.snakemap.pick_open_hex()
                if start_pos:	# Found a valid starting position
                    self.next_snake_id += 1
                    self.main_color = change_color(self.main_color, 0.1)
                    self.snakemap.put_snake_value(start_pos, self.next_snake_id)
                    new_snake = Snake(self.hexes, self.main_color, self.next_snake_id, start_pos)
                    self.live_snakes[self.next_snake_id] = new_snake

            for id, snake in self.live_snakes.items():
                if snake.alive:
                    snake.draw_snake()  # Draw the snake head

                    # Try to move the snake
                    next_pos = helpfunc.hex_in_direction(snake.pos, snake.direction)  # Get the coord of where the snake will go
                    if self.snakemap.is_open_hex(next_pos):  # Is the new spot open?
                        snake.pos = next_pos  # Yes, update snake position
                        self.snakemap.put_snake_value(snake.pos, snake.snakeID)  # Put snake on the virtual snake map
                    else:
                        dirs = self.snakemap.get_valid_directions(snake.pos)  # Blocked, check possible directions

                        if dirs:	# Are there other places to go?
                            snake.direction = choice(dirs)  # Yes, pick a random new direction
                            snake.pos = helpfunc.hex_in_direction(snake.pos, snake.direction)
                            self.snakemap.put_snake_value(snake.pos, snake.snakeID)
                        else:	# No directions available
                            snake.alive = False		# Kill the snake
                            self.snakemap.remove_snake_path(snake.snakeID)	# Snake is killed

            yield self.speed  	# random time set in init function