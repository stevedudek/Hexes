from random import random, randint, choice

from color import random_color, random_color_range, gradient_wheel
from HelperFunctions import neighbors, hex_ring, hex_in_direction, get_close_dir, all_dir, get_nearest, rand_dir, \
    get_random_hex
from hex import HEX_SIZE, NUM_HEXES


class Bullet(object):
    def __init__(self, hexmodel, pos, color, direction, atten):
        self.hexes = hexmodel
        self.color = color
        self.direction = direction
        self.pos = pos
        self.atten = atten
        self.intense = 1

    def draw_bullet(self):
        self.hexes.set_cell(self.pos, gradient_wheel(self.color, self.intense))

    def move_bullet(self):
        self.pos = hex_in_direction(self.pos, self.direction)  # Where is the bullet shooting?
        self.intense -= self.atten
        return self.intense > 0


class Asteroid(object):
    def __init__(self, hexmodel):
        self.hexes = hexmodel
        self.h = get_random_hex()
        self.color = random_color()
        self.pos = choice(hex_ring(center=(self.h, 0, 0), size=HEX_SIZE))
        self.direction = get_close_dir(self.pos, (self.h, 0, 0))  # Aim Asteroid towards the middle
        self.speed = randint(1, 5) / 5.0
        self.curr_pos = 0.0
        self.size = randint(2, 3)

    def draw_asteroid(self):
        self.hexes.set_cell(self.pos, self.color)  # Draw the center

        # Draw the outer rings
        for ring in range(self.size):
            self.hexes.set_cells(hex_ring(self.pos, ring),
                                 gradient_wheel(self.color, 1 - (0.2 * (ring + 1))))

    def move_asteroid(self):
        self.curr_pos += self.speed
        if self.curr_pos >= 1.0:
            self.curr_pos -= 1.0
            self.pos = hex_in_direction(self.pos, self.direction)
            # return True
            return self.pos not in hex_ring(center=(self.h, 0, 0), size=HEX_SIZE + 2)
        return True

    def get_hexes(self):
        return [coord for ring in range(1, self.size)
                for coord in hex_ring(self.pos, ring)] + [self.pos]


class Ship(object):
    def __init__(self, hexmodel, h):
        self.hexes = hexmodel
        self.h = h
        self.pos = (h, randint(-2,2),randint(-2,2))
        self.color = random_color()
        self.direction = rand_dir()
        self.turny = 3
        self.speedy = 15
        self.shooty = 3

    def get_hexes(self):
        return neighbors(self.pos) + [hex_in_direction(self.pos, self.direction, 2), self.pos]

    def draw_ship(self):

        # Draw the body
        ship_cells = [hex_in_direction(self.pos, direction) for direction in all_dir()
                      if direction != (self.direction + 3) % 6]
        self.hexes.set_cells(ship_cells, self.color)

        # Draw the nozzle
        self.hexes.set_cell(hex_in_direction(self.pos, self.direction, 2), self.color)

        # Draw the center body
        self.hexes.set_cell(self.pos, gradient_wheel(self.color, 0.2))

    def move_ship(self, bull_array, ast_pos):

        near_ast = get_nearest(self.pos, ast_pos)
        self.direction = get_close_dir(self.pos, near_ast)

        # Moving forward
        if not randint(0, self.speedy):
            new_spot = hex_in_direction(self.pos, self.direction)
            if new_spot not in hex_ring((self.h, 0, 0), 4):
                self.pos = new_spot

        # Shooting
        if not randint(0, self.shooty):
            bull_array.append(Bullet(hexmodel=self.hexes, pos=hex_in_direction(self.pos, self.direction, 3),
                                     color=self.color, direction=self.direction, atten=0.1))


class Asteroids(object):
    def __init__(self, hexmodel):
        self.name = "Asteroids"
        self.hexes = hexmodel
        self.ships = []  # List that holds Ship objects
        self.bullets = []  # List that holds Bullet objects
        self.asteroids = []  # List that holds Asteroid objects
        self.speed = 0.1

    def next_frame(self):

        while True:

            ship_hex_numbers = [ship.h for ship in self.ships]
            hexes_without_ships = [h for h in range(NUM_HEXES) if h not in ship_hex_numbers]
            for h in hexes_without_ships:
                new_ship = Ship(hexmodel=self.hexes, h=h)
                self.ships.append(new_ship)

            if len(self.asteroids) < 3 * NUM_HEXES:
                self.asteroids.append(Asteroid(self.hexes))

            self.hexes.black_all_cells()
            self.draw_ships()
            self.draw_asteroids()
            self.draw_bullets()
            self.collisions()

            yield self.speed

    def draw_ships(self):
        for s in self.ships:
            s.move_ship(self.bullets, self.get_ast_pos())
            s.draw_ship()

    def draw_asteroids(self):
        for a in self.asteroids:
            a.draw_asteroid()
            if not a.move_asteroid():
                self.asteroids.remove(a)  # Remove from list

    def draw_bullets(self):
        for b in self.bullets:
            b.draw_bullet()
            if not b.move_bullet():
                self.bullets.remove(b)

    def get_ast_pos(self):
        return [a.pos for a in self.asteroids]

    def collisions(self):
        # Check bullet - asteroid overlap
        for b in self.bullets:
            for a in self.asteroids:
                if set([b.pos]).intersection(a.get_hexes()):  # Does bullet b collide with asteroid a?
                    self.asteroids.remove(a)
                    self.bullets.remove(b)
                    for direction in all_dir():
                        new_bullet = Bullet(self.hexes, a.pos, a.color, direction, 0.33)
                        self.bullets.append(new_bullet)
                    break

        # Check ship - asteroid overlap
        all_asteroid_cells = sum([a.get_hexes() for a in self.asteroids], [])
        for ship in self.ships:
            if set(ship.get_hexes()).intersection(all_asteroid_cells):
                self.ships.remove(ship)  # Explode ship
                for direction in all_dir():
                    new_bullet = Bullet(self.hexes, ship.pos, ship.color, direction, 0.33)
                    self.bullets.append(new_bullet)
