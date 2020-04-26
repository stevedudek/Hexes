"""
Model to communicate with a Hex simulator over a TCP socket

"""
from random import choice, randint
from pixel import Pixel

NUM_HEXES = 2
HEX_SIZE = 11    # Number of LEDs high/wide for each hex
HEX_OFFSET = 5

"""
March 2020 Changes
1. Hexes

July 2019 Changes
1. Implement Pixel class in place of hash table

Nov 2018 Changes
1. No more fades to black, so removed "fract" variable below
2. Added send_intensity()

Parameters for each Hex: (X, Y)
"""


class Hex(object):
    """
    Hex object (= hex model) represents all LEDs (so all giant hexes)
    Each Hex is composed of Pixel objects

    Hash table for { coordinate: pixel object }
    Hex coordinates (hex, x, y) are the keys
    Pixel objects are the values
    """
    def __init__(self):
        self.cellmap = self.add_hexes()  # { coord: pixel object }

    def __repr__(self):
        return "{} Hexes: {} x {}".format(self.hexes, self.size, self.size)

    @property
    def hexes(self):
        return NUM_HEXES

    @property
    def hex_offset(self):
        return HEX_OFFSET

    @property
    def size(self):
        return HEX_SIZE

    def all_cells(self):
        """Get all valid coordinates"""
        return self.cellmap.keys()

    def all_pixels(self):
        """Get all pixel objects"""
        return self.cellmap.values()

    def all_onscreen_pixels(self):
        return [pixel for pixel in self.all_pixels() if pixel.cell_exists()]

    def cell_exists(self, coord):
        """True if the coordinate is valid"""
        return coord in self.cellmap

    def get_pixel(self, coord):
        """Get the pixel object associated with the (h,x,y) coordinate"""
        return self.cellmap.get(coord)

    def inbounds(self, coord):
        """Is the coordinate inbounds?"""
        (h,x,y) = coord
        return 0 <= h < self.hexes and 0 <= x < self.size and 0 <= y < self.size

    def set_cell(self, coord, color):
        """Set the pixel at coord (h,x,y) to color hsv"""
        if self.cell_exists(coord):
            self.get_pixel(coord).set_color(color)

    def set_cells(self, coords, color):
        """Set the pixels at coords to color hsv"""
        for coord in coords:
            self.set_cell(coord, color)

    def set_all_cells(self, color):
        """Set all cells to color hsv"""
        for pixel in self.all_onscreen_pixels():
            pixel.set_color(color)

    def black_cell(self, coord):
        """Blacken the pixel at coord (h,x,y)"""
        if self.cell_exists(coord):
            self.get_pixel(coord).set_black()

    def black_cells(self, coords):
        """Black the pixels at coords to color hsv"""
        for coord in coords:
            self.black_cell(coord)

    def black_all_cells(self):
        """Blacken all pixels"""
        for pixel in self.all_onscreen_pixels():
            pixel.set_black()

    def clear(self):
        """Force all cells to black"""
        for pixel in self.all_onscreen_pixels():
            pixel.force_black()

    def push_next_to_current_frame(self):
        """Push the next frame back into the current frame"""
        for pixel in self.all_onscreen_pixels():
            pixel.push_next_to_current_frame()

    def interpolate_frame(self, fraction):
        """Dump the current frame into the interp frame"""
        for pixel in self.all_onscreen_pixels():
            pixel.interpolate_frame(fraction)

    #
    # Setting up the Hex
    #
    def add_hexes(self):
        """cellmap is a dictionary of { coord: pixel object }"""
        cellmap = {}

        for h in range(self.hexes):
            for x in range(-self.hex_offset, self.hex_offset + 1):
                y_adj = -(self.hex_offset + x) if x < 0 else -self.hex_offset
                for y in range(self.size - abs(x)):
                    cellmap[(h, x, y + y_adj)] = Pixel(h, x, y + y_adj)
        return cellmap

    def rand_cell(self, hex_number=None):
        """Pick a random coordinate"""
        if hex_number is None:
            return choice(list(self.cellmap.keys()))
        return choice([(h, x, y) for (h, x, y) in self.cellmap.keys() if h == hex_number])

    def rand_hex(self):
        """Pick a random big hex number"""
        return randint(0, self.hexes)


"""
hex cell primitives
"""


def neighbors(coord):
    """Returns a list of the four neighboring tuples at a given coordinate"""
    (x,y) = coord

    _coords = [ (0, 1), (1, 0), (0, -1), (-1, 0) ]

    return [(x+dx, y+dy) for (dx,dy) in _coords]


def touch_neighbors(coord):
    """Returns a list of the eight neighboring tuples at a given coordinate"""
    (x,y) = coord

    _coords = [ (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1) ]

    return [(x+dx, y+dy) for (dx,dy) in _coords]


def hex_in_line(coord, direction, distance=0):
    """
    Returns the coord and all pixels in the direction along the distance
    """
    return [hex_in_direction(coord, direction, x) for x in range(distance)]


def hex_in_direction(coord, direction, distance=1):
    """
    Returns the coordinates of the cell in a direction from a given cell
    Direction is indicated by an integer
    """
    for i in range(distance):
        coord = hex_nextdoor(coord, direction)
    return coord


def hex_nextdoor(coord, direction):
    """
    Returns the coordinates of the hex cell in the given direction
    Coordinates determined from a lookup table
    """
    _lookup = [ (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1) ]

    (x,y) = coord
    (dx,dy) = _lookup[(direction % len(_lookup))]
    
    return (x+dx, y+dy)


def get_rand_neighbor(coord):
    """
    Returns a random neighbors
    Neighbor may not be in bounds
    """
    return choice(neighbors(coord))


def hex_shape(coord, size):
    """
    Get the cells of a hex whose lower-left corner is at coord
    """
    (x_ll, y_ll) = coord
    return [(x + x_ll, y + y_ll) for x in range(size) for y in range(size)]


def mirror_coords(coord, sym=4):
    """
    Return the 1, 2, or 4 mirror coordinates
    """
    if sym == 1:
        return [coord]

    (x, y) = coord
    x_offset, y_offset = x % HEX_SIZE, y % HEX_SIZE
    x_ll, y_ll = x - x_offset, y - y_offset

    if sym == 2:
        return [(x_offset + x_ll, y_offset + y_ll), (HEX_SIZE - y_offset + x_ll, HEX_SIZE - x_offset + y_ll)]
    else:
        return [(x_offset + x_ll, y_offset + y_ll), (y_offset + x_ll, HEX_SIZE - x_offset + y_ll),
                (HEX_SIZE - y_offset + x_ll, HEX_SIZE - x_offset + y_ll), (HEX_SIZE - y_offset + x_ll, x_offset + y_ll)]
