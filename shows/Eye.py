from random import randint
from color import rgb_to_hsv, random_hue, random_color, gradient_wheel, hue_to_color
from HelperFunctions import hex_ring, hex_in_direction, neighbors, hex_line_in_direction, one_in, rand_dir
from hex import NUM_HEXES


class Eyes(object):
    def __init__(self, hexmodel):
        self.name = "Eyes"
        self.hexes = hexmodel
        self.eyes = [Eye(i, hexmodel) for i in range(NUM_HEXES)]
        self.speed = 0.1

    def next_frame(self):

        while True:
            self.hexes.set_all_cells(rgb_to_hsv((255, 255, 255)))  # Set background to white

            for eye in self.eyes:
                eye.draw_ball()
                eye.draw_lids()
                eye.draw_rays()
                eye.wink()
                eye.move_eye_ball()
                eye.update_rays()

            yield self.speed  # random time set in init function


class Eye(object):
    def __init__(self, hex_number, hexmodel):
        self.h = hex_number
        self.hexes = hexmodel
        self.ball_color = hue_to_color(100)
        self.face_color = hue_to_color(50)
        self.ball_pos = (self.h, 0, 0)
        self.lid_pos = 4
        self.lid_move = 0
        self.ball_move = 0
        self.big_ball = False
        self.ray = -1
        self.ray_pos = (self.h, 0, 0)
        self.ray_color = 0

    def wink(self):
        if self.lid_move == 0:
            if one_in(20):
                self.lid_move = -1
        elif self.lid_move == -1:
            self.lid_pos -= 1
            if self.lid_pos <= 0:
                self.lid_move = 1
        else:
            self.lid_pos += 1
            if self.lid_pos >= 4:
                self.lid_move = 0

    def move_eye_ball(self):
        if self.ball_move == 10:
            if one_in(30):
                self.ball_move = rand_dir()
        else:
            self.ball_pos = hex_in_direction(self.ball_pos, self.ball_move)
            if self.ball_pos in hex_ring((self.h, 0, 0), 3):
                self.ball_move = (self.ball_move + 3) % 6
            if self.ball_pos == (self.h, 0, 0):
                self.ball_move = 10
            if self.ray == -1:
                self.ray_pos = self.ball_pos
                self.ray = 0	# Start the eye-ray
                self.ray_color = random_hue()

            if one_in(20):
                self.big_ball = not self.big_ball  # Change pupil size

    def update_rays(self):
        if self.ray != -1:
            self.ray += 1
            if self.ray >= 12:
                self.ray = -1

    def draw_ball(self):
        self.hexes.set_cell((self.h, 0 ,0), self.ball_color)  # Draw the center
        self.hexes.set_cells(hex_ring(self.ball_pos, 2), gradient_wheel(self.ball_color, 0.6))
        if self.big_ball:
            self.hexes.black_cells(hex_ring(self.ball_pos, 1))
        else:
            self.hexes.set_cells(hex_ring(self.ball_pos, 1), gradient_wheel(self.ball_color, 0.8))

    def draw_lids(self):
        for i in range(self.lid_pos, 6):
            atten = 1 - ( (self.lid_pos - i) * 0.15)
            color = gradient_wheel(self.face_color, atten)
            self.draw_line( (self.h, 0, -i), 0, 6, color)
            self.draw_line( (self.h, 0, -i), 4, 6, color)
            self.draw_line( (self.h, 0,  i), 3, 6, color)
            self.draw_line( (self.h, 0,  i), 1, 6, color)

    def draw_rays(self):
        if self.ray == -1:
            return

        if self.ray > 7:
            start_on = self.ray - 7
            end_on = 7
        else:
            start_on = 0
            end_on = self.ray

        for i in range(start_on, end_on):
            center = hex_in_direction(self.ray_pos, 5, i)
            hue = (self.ray_color + (i * 2)) % 255
            dim_color = gradient_wheel(hue_to_color(hue), 1 - (i * 0.1))
            self.draw_line(center, 3, i, dim_color)
            self.draw_line(center, 1, i, dim_color)

    def draw_line(self, start, direction, length, color):
        self.hexes.set_cells(hex_line_in_direction(start, direction, length), color)