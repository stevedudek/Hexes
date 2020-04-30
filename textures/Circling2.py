from color import random_hue, gradient_wheel, hue_to_color
import HelperFunctions as helpfunc


class Planet(object):
    def __init__(self, hexmodel, pos, center, color, direction):
        self.hexes = hexmodel
        self.pos = pos
        self.color = color
        self.direction = direction
        self.center = center
        self.trails = helpfunc.Faders(hexmodel)

    def draw_planet(self):

        self.trails.cycle_faders(refresh=False)
        self.trails.add_fader(color=hue_to_color(self.color), pos=self.pos, intense=1.0, growing=False, change=0.25)

        # Draw a middle ring
        gradient_color = gradient_wheel(hue_to_color(self.color), 0.9)
        for coord in helpfunc.hex_ring(self.pos, 1):
            self.trails.add_fader(color=gradient_color, pos=coord, intense=0.9, growing=False, change=0.25)

        # Draw an outer ring
        gradient_color = gradient_wheel(hue_to_color(self.color), 0.7)
        for coord in helpfunc.hex_ring(self.pos, 2):
            self.trails.add_fader(color=gradient_color, pos=coord, intense=0.7, growing=False, change=0.25)

    def move_planet(self):
        self.pos = helpfunc.clock_cell(self.pos, self.direction, self.center)
        self.color += 10


class Circling2(object):
    def __init__(self, hexmodel):
        self.name = "Circling2"
        self.hexes = hexmodel
        self.planets = []  # List that holds Planet objects
        self.speed = 0.2
        self.color = random_hue()

    def next_frame(self):

        for h in helpfunc.all_hexes():
            center = helpfunc.get_center(h)
            color_offset = (self.color + 40) % 255
            self.planets += [Planet(self.hexes, (h, 0, 6), center, self.color, 1),
                             Planet(self.hexes, (h, 6, 0), center, color_offset, -1),
                             Planet(self.hexes, (h, 0, 3), center, self.color, 1),
                             Planet(self.hexes, (h, 3, 0), center, color_offset, -1)]

        while True:

            self.hexes.black_all_cells()

            for planet in self.planets:
                planet.draw_planet()
                planet.move_planet()

            self.color = (self.color + 1) % 255

            yield self.speed
