from random import randint
from color import gradient_wheel
from math import sqrt
from hex import HEX_SIZE, HEX_OFFSET, NUM_HEXES

#
# Constants
#
MAX_COLOR = 1536
MAX_DIR = 6
MAX_HUE = 255


#
# Common random functions
#
def one_in(chance):
    """Random chance. True if 1 in Number"""
    return randint(1, chance) == 1


def get_random_hex():
    """Get a random big hex"""
    return randint(0, NUM_HEXES-1)


def get_random_center():
    """Get a random hex center"""
    return get_center(get_random_hex())


def plus_or_minus():
    """Return either 1 or -1"""
    return (randint(0,1) * 2) - 1


def up_or_down(value, amount, min, max):
    """Increase or Decrease a counter with a range"""
    value += (amount * plus_or_minus())
    return bounds(value, min, max)


def inc(value, increase, min, max):
    """Increase/Decrease a counter within a range"""
    value += increase
    return bounds(value, min, max)


def bounds(value, minimum, maximum):
    """Keep value between min and max"""
    return max([minimum, min([value, maximum]) ])


#
# Directions
#
def all_hexes():
    """Get a list of all hexes"""
    return range(NUM_HEXES)


def all_centers():
    """Get a list of all center hexes"""
    return [get_center(h) for h in all_hexes()]


def all_dir():
    """Get all directions"""
    return range(MAX_DIR)


def rand_dir():
    """Get a random direction"""
    new_dir = randint(0, MAX_DIR - 1)
    return new_dir


def rand_straight_dir():
    return randint(0, 3) * 2


def turn_left(direction):
    """Return the left direction"""
    return (MAX_DIR + direction - 1) % MAX_DIR


def turn_right(direction):
    """Return the right direction"""
    return (direction + 1) % MAX_DIR


def turn_left_or_right(direction):
    """Randomly turn left or right"""
    return turn_left(direction) if one_in(2) else turn_right(direction)


def get_close(coord, center):
    """Returns the neighboring cell of coord that is closest to the center"""
    return get_nearest(coord, hex_ring(center, 1)) if coord != center else center


def get_close_dir(coord, center):
    """Returns the direction from coord that is closest to the center"""
    close_cell = get_close(center, coord)
    for direction in range(MAX_DIR):
        if close_cell == hex_in_direction(coord, direction):
            return direction
    print("Something wrong with get_closer_dir() in HelperFunctions")
    return 0  # Something went wrong


def clock_cell(coord, direction, center):
    """Returns the cell clockwise (1) or counterclockwise (-1)
       from the given cell and center coordinate"""
    if direction not in [-1, 0, 1]:
        raise ValueError("direction {} not -1, 0, or 1".format(direction))
    if direction == 0 or coord == center:
        return coord

    for i in range(0, 8):
        ring_cells = hex_ring(center, i)
        index = find_element_in_list(coord, ring_cells)
        if index == -1:  # not found
            continue
        return ring_cells[(index + direction) % len(ring_cells)]
    return coord  # Something's wrong


def find_element_in_list(element, list_element):
    """Pull the index of the element or -1 if not found"""
    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return -1


def get_dist(coord1, coord2):
    """Get the distance between two coordinates"""
    h1, x1, y1 = coord1
    h2, x2, y2 = coord2
    return (abs(x1 - x2) + abs(y1 - y2) + abs(x1 + y1 - x2 - y2)) / 2.0


def get_nearest(center, coords):
    """Returns the nearest coord cell to the center"""
    return sorted(coords, key=lambda cell: get_dist(center, cell))[0]


#
# Hex cell primitives
#
def get_center(hex_number):
    """Return center hex"""
    return (hex_number, 0, 0)


def neighbors(coord):
    """Returns a list of the six hexes neighboring a tuple at a given coordinate"""
    _neighbors = [ (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1) ]

    (h, x, y) = coord
    return [(h, x + dx, y + dy) for (dx, dy) in _neighbors]


def next_neighbors(coord):
    _next_neighbors = [ (1, -2), (2, -1), (1, 1), (-1, 2), (-2, 1), (-1, -1) ]

    (h, x, y) = coord
    return [(h, x + dx, y + dy) for (dx, dy) in _next_neighbors]


def hex_in_direction(coord, direction, distance=1):
    """
    Returns the coordinates of the hex in a direction from a given hex.
    Direction is indicated by an integer:

     2  /\  1
     3 |  | 0
     4  \/  5
    """
    for i in range(distance):
        coord = neighbors(coord)[direction]
    return coord


def hex_line_in_direction(coord, direction, distance):
    return [hex_in_direction(coord, direction, i) for i in range(distance)]


def hex_ring(center, size):
    """Returns a list of coordinates that make up a ring centered around a hex"""
    if size == 0:
        return center
    h = hex_in_direction(center, 4, size)
    results = []
    for i in range(0, 6):
        for j in range(0, size):
            results.append(h)
            h = neighbors(h)[i]
    return results


def get_edge_ring(h):
    """Return all the coordinates on the outer edge of the big Hex h"""
    return hex_ring(center=(h, 0, 0), size=HEX_OFFSET)


def mirror_hexes(coord):
    """Find the five other mirrored hexes for a given hex"""
    coords = [coord]
    for i in range(5):
        coord = rotate_left(coord)
        coords.append(coord)
    return coords


def rotate_left(coord):
    (p, q, r) = coord
    (x, y, z) = (q, r, -q - r)  # Convert to cube coordinates
    (left_x, left_y, left_z) = (-z, -x, -y)  # Convert back to axial coordinates
    return (p, left_x, left_y)


def rotate_right(coord):
    (p, q, r) = coord
    (x, y, z) = (q, r, -q - r)  # Convert to cube coordinates
    (right_x, right_y, right_z) = (-y, -z, -x)  # Convert back to axial coordinates
    return (right_x, right_y)


def get_box(coord, width, height, up=True):
    """Returns a list of cells within a box:
       (x,y coord of the lower left corner), width, height"""
    direction = 1 if up else 0

    line = hex_line_in_direction(coord=coord, direction=2, distance=height)
    return sum([hex_line_in_direction(coord=coord, direction=direction, distance=width) for coord in line], [])

#
# Colors
#
def rand_color(reds=False):
    """return a random, saturated hsv color. reds are 192-32"""
    _hue = randint(192, 287) % 255 if reds else randint(0, 255)
    return _hue, 255, 255


def byte_clamp(value, wrap=False):
    """Convert value to int and clamp between 0-255"""
    if wrap:
        return int(value) % 255
    else:
        return max([ min([int(value), 255]), 0])


#
# Fader class and its collection: the Faders class
#
class Faders(object):
    def __init__(self, hexmodel):
        self.hex = hexmodel
        self.fader_array = []

    def __del__(self):
        del self.fader_array

    def add_fader(self, color, pos, intense=1.0, growing=False, change=0.25):
        new_fader = Fader(self.hex, color, pos, intense, growing, change)
        self.fader_array.append(new_fader)

    def cycle_faders(self, refresh=True):
        if refresh:
            self.hex.black_all_cells()

        # Draw, update, and kill all the faders
        for f in self.fader_array:
            if f.is_alive():
                f.draw_fader()
                f.fade_fader()
            else:
                f.black_cell()
                self.fader_array.remove(f)

    def num_faders(self):
        return len(self.fader_array)

    def fade_all(self):
        for f in self.fader_array:
            f.black_cell()
            self.fader_array.remove(f)  # Look for a delete object method


class Fader(object):
    def __init__(self, hexmodel, color, pos, intense=1.0, growing=False, change=0.25):
        self.hex = hexmodel
        self.pos = pos
        self.color = color
        self.intense = intense
        self.growing = growing
        self.decrease = change

    def draw_fader(self):
        self.hex.set_cell(self.pos, gradient_wheel(self.color, self.intense))

    def fade_fader(self):
        if self.growing:
            self.intense += self.decrease
            if self.intense > 1.0:
                self.intense = 1.0
                self.growing = False
        else:
            self.intense -= self.decrease
            if self.intense < 0:
                self.intense = 0

    def is_alive(self):
        return self.intense > 0

    def black_cell(self):
        self.hex.black_cell(self.pos)

