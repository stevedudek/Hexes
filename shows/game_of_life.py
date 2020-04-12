from color import random_hue, hue_to_color, random_color, black, change_color
from random import random, randint

import HelperFunctions as helpfunc


class LifeModel(object):
    def __init__(self, hexmodel):
        # similar to the Hex Model
        # this model contains a dictionary of hex coordinates
        # but the life model can be of arbitrarily large size
        # Hexes are tiled in a regular hexagon
        # Primary data stored is whether the hex is "alive" or not"

        self.hexes = hexmodel
        self.life_map = {}

    def add(self, coord):
        """Add a new life hex to the dictionary/model at given coordinate"""
        self.life_map[coord] = LifeHex()

    def get(self, coord, default=None):
        """Returns a lifehex object for a coordinate. Return 'default' if not found"""
        # print(coord)
        return self.life_map.get(coord, default)

    def cell_exists(self, coord):
        """Check if a life hex exists at a given coordinate"""
        return coord in self.life_map.keys()

    def decide_fate(self, coord):
        cell = self.get(coord)
        value = self.calc_next_life(coord)

        if cell.is_alive:
            if 2.0 <= value <= 3.3:
                cell.revive()
            else:
                cell.kill()  # too many or too few neighbors
        else:
            if 2.3 <= value < 2.9:
                cell.revive()
            else:
                cell.kill()

    def calc_next_life(self, coord):
        return self.num_alive_neighbors(coord) + (self.num_alive_next_neighbors(coord) * 0.3)

    def num_alive_neighbors(self, coord):
        return self.num_alive_hexes(helpfunc.neighbors(coord))
    
    def num_alive_next_neighbors(self, coord):
        return self.num_alive_hexes(helpfunc.next_neighbors(coord))
    
    def num_alive_hexes(self, coords):
        i = 0
        for coord in coords:
            if self.cell_exists(coord):
                cell = self.get(coord)
                if cell.is_alive():
                    i += 1
            else: i += 0.5  # boundary cells treated as half-alive
        return i

    def __repr__(self):
        return str(self.life_map)


class LifeHex(object):
    """Life Model is composed of these LifeHexes
       A life hex is just a convenient shorthand to hold 2 booleans in each hex"""
    def __init__(self):
        self.on = random() < 0.2
        self.next_on = False

    def revive(self):
        self.next_on = True

    def kill(self):
        self.next_on = False

    def is_alive(self):
        return self.on

    def push_state(self):
        self.on = self.next_on


class GameOfLife(object):

    def __init__(self, hexmodel):
        self.name = "Game of Life"        
        self.hexes = hexmodel  # Actual visualized hexes
        self.life_hexes = self.create_life_model(size=8)  # Virtual life hexes
        self.speed = 0.2 + (random() * 2)
        self.on_color = random_color()
        
        # Most of the time set the background to black
        # Some of the time choose a colored background
        self.off_color = random_color() if helpfunc.one_in(5) else black()
        
    def next_frame(self):

        for i in range (0,1000): # number of steps per game

            # Calculate each hex's fate
            for cell in self.life_hexes.life_map:
                self.life_hexes.decide_fate(cell)

            # Push all at once the new fates into current state
            for cell in self.life_hexes.life_map:
                self.life_hexes.get(cell).push_state()

            # Draw the actual hexes, but only the ones in the display
            for cell in self.hexes.cellmap.keys():
                mapped_cell = self.life_hexes.get(cell)
                if mapped_cell:
                    color = self.on_color if mapped_cell.is_alive() else self.off_color
                    self.hexes.set_cell(cell, color)

            # Slowly change the colors
            if helpfunc.one_in(10):
                self.on_color = change_color(self.on_color, 0.1)

            if helpfunc.one_in(5):
                if self.off_color != black():  # Black - keep as black
                    self.off_color = change_color(self.off_color, -0.05)

            yield self.speed  # random time set in init function

    def create_life_model(self, size):
        life_model = LifeModel(self.hexes)

        for h in helpfunc.all_hexes():
            center = helpfunc.get_center(h)
            life_model.add(center)
            for ring in range(1, size + 1):
                for coord in helpfunc.hex_ring(center, ring):
                    life_model.add(coord)

        return life_model



