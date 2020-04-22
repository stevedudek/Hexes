"""
Reworking LED code to use a Pixel class

A LED-contraption object, like a Hex, is composed of Pixel objects
A Pixel holds only 1 LED
A Pixel knows coordinates: (h, x, y) coordinate, (strip, LED) coordinate, DMX address
              colors: current-frame color, next-frame color, interp color, (x2 if dual channel)
Pulling the layout logic out of Processing and into this class
"""
import color as color

# Convert (x, y) coordinate into LED position. Includes buffer LEDs.
LED_LOOKUP = [
    [-1, -1, -1, -1, -1, 55, 59, 60, 94, 93, 98],
    [-1, -1, -1, -1, 54, 53, 61, 62, 92, 91, 99],
    [-1, -1, -1, 16, 52, 51, 63, 64, 90, 89, 101],
    [-1, -1, 17, 18, 50, 49, 65, 66, 88, 87, 102],
    [-1, 12, 19, 20, 48, 47, 67, 68, 86, 85, 104],
    [11, 10, 21, 22, 46, 45, 69, 70, 84, 83, 105],
    [9, 8, 23, 24, 44, 43, 71, 72, 82, 81, -1],
    [7, 6, 25, 26, 42, 41, 73, 74, 80, -1, -1],
    [5, 4, 27, 28, 40, 39, 75, 76, -1, -1, -1],
    [3, 2, 29, 30, 38, 37, 77, -1, -1, -1, -1],
    [1, 0, 31, 32, 36, 35, -1, -1, -1, -1, -1]
]


class Pixel(object):
    """
    Pixel colors are hsv [0-255] triples (very simple)
    """

    def __init__(self, h, x, y):
        self.h, self.x, self.y = h, x, y  # h = hex number = strip = universe
        self.led = self.get_led()
        self.curr_frame = color.almost_black()
        self.next_frame = color.black()
        self.interp_frame = color.black()

    def get_coord(self):
        return self.h, self.x, self.y

    def get_universe_index(self):
        """Return a tuple of (universe, index)"""
        return self.h + 1, self.led * 3

    def cell_exists(self):
        return self.led != -1

    def has_changed(self):
        return color.are_different(self.curr_frame, self.next_frame)

    def set_color(self, color):
        self.next_frame = color

    def set_next_frame(self, color):
        self.next_frame = color

    def set_curr_frame(self, color):
        self.curr_frame = color

    # def push_current_to_interp_frame(self):
    #     self.interp_frame = self.curr_frame

    # def push_next_to_interp_frame(self):
    #     self.interp_frame = self.next_frame

    def interpolate_frame(self, fraction):
        self.interp_frame = color.interp_color(self.curr_frame, self.next_frame, fraction)

    def set_black(self):
        self.next_frame = color.black()

    def force_black(self):
        self.curr_frame = color.almost_black()
        self.set_black()

    def push_next_to_current_frame(self):
        self.next_frame = self.curr_frame

    def get_led(self):
        """Convert (h, x, y) coordinate to (strip, led) coordinate"""
        assert -5 <= self.x <= 5 and \
               -5 <= self.y <= 5, \
            "hex coordinate ({}, {}) out of bounds".format(self.x, self.y)
        return LED_LOOKUP[self.x + 5][self.y + 5]
