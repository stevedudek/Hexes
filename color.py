import colorsys
from random import random, randint

"""
Color

JULY 2019

REWROTE and SIMPLIFIED
1. Make HSV [0-255]
2. Colors are now just triples of (hue, sat, value)

JULY 2019
Consider rewriting this API to use less memory
Remove unused functions
Try to keep the surrounding API
"""


def _float_to_byte(f):
    """Convert a [0.0-1.0] float to a [0-255] byte"""
    return int(f * 255) % 256


def _float_to_byte_triple(triple):
    """Convert 3 [0.0-1.0] floats to 3 [0-255] bytes"""
    return _float_to_byte(triple[0]), _float_to_byte(triple[1]), _float_to_byte(triple[2]) 

    
def _byte_to_float(b):
    """Convert a [0-255] byte to a [0.0 - 1.0] float"""
    return (int(b) % 256) / 255.0


def _byte_to_float_triple(triple):
    """Convert 3 [0-255] bytes to 3 [0.0-1.0] floats"""
    return _byte_to_float(triple[0]), _byte_to_float(triple[1]), _byte_to_float(triple[2])


def rgb_to_hsv(rgb):
    """convert a rgb[0-255] tuple to hsv[0-255]"""
    _r, _g, _b = _byte_to_float_triple(rgb)
    return _float_to_byte_triple(colorsys.rgb_to_hsv(_r, _g, _b))


def hsv_to_rgb(hsv):
    """convert a hsv[0-255] tuple to rgb[0-255]"""
    _h, _s, _v = _byte_to_float_triple(hsv)
    return _float_to_byte_triple(colorsys.hsv_to_rgb(_h, _s, _v))


def hue_to_color(hue):
    """Turn a 0-255 hue into a saturate hsv color"""
    return hue, 255, 255


def black():
    """Return black color"""
    return 255, 255, 0


def almost_black():
    """Return black color"""
    return 254, 255, 0


def white():
    """Return white color"""
    return 0, 0, 255


def random_color(reds=False):
    """return a random, saturated hsv color. reds are 192-32"""
    _hue = randint(192, 287) % 255 if reds else randint(0, 255)
    return _hue, 255, 255


def random_color_range(hsv, shift_range=0.3):
    """Returns a random color around a given color within a particular range
       Function is good for selecting blues, for example"""
    _delta_h = (random() - 0.5) * min([0.5, shift_range]) * 2
    _new_h = _float_to_byte( _byte_to_float(hsv[0]) + _delta_h)
    return _new_h, hsv[1], hsv[2]


def random_hue(reds=False):
    """return a random hue. reds are 192-32"""
    return randint(192, 287) % 255 if reds else randint(0, 255)


def gradient_wheel(hsv, intensity):
    """Dim an hsv color with v=intensity [0.0-1.0]"""
    intensity = max([min([intensity, 1]), 0])
    return hsv[0], hsv[1], _float_to_byte(intensity)


def change_color(hsv, amount):
    """Change color by a 0.0-1.0 range. Amount can be negative"""
    return (hsv[0] + _float_to_byte(amount)), hsv[1], hsv[2]


def interp_color(hsv1, hsv2, fraction):
    """Interpolate between hsv1 (fract 0) and hsv2 (fract 1.0) """
    if fraction <= 0:
        return hsv1
    elif fraction >= 1:
        return hsv2
    elif not are_different(hsv1, hsv2):
        return hsv1
    elif hsv1[2] == 0:  # 1 is black, so dim 2
        return dim_color(hsv2, fraction)
    elif hsv2[2] == 0:  # 2 is black, so dim 1
        return dim_color(hsv1, 1 - fraction)
    else:
        return  interp_wrap(hsv1[0], hsv2[0], fraction), \
               interp_value(hsv1[1], hsv2[1], fraction), \
               interp_value(hsv1[2], hsv2[2], fraction)


def mix_color_and_texture(hsv1, hsv2, fraction):
    """Get color from hsv1 and value from hsv2"""
    return hsv1[0], hsv1[1], interp_value(hsv1[2], hsv2[2], 1 - fraction)


def interp_value(v1, v2, fraction):
    return int(v1 + (fraction * (v2 - v1)))


def interp_wrap(a, b, fraction):
    if a >= b:
        dist_clockwise = 256 + b - a
        dist_counterclockwise = a - b
    else:
        dist_clockwise = b - a
        dist_counterclockwise = 256 + a - b

    if dist_clockwise <= dist_counterclockwise:
        answer = a + (dist_clockwise * fraction)
    else:
        answer = a - (dist_counterclockwise * fraction)

    return answer


def are_different(color1, color2):
    """Are the two colors different?"""
    return color_to_int(color1[0], color1[1], color1[2]) != color_to_int(color2[0], color2[1], color2[2])


def restrict_color(hsv, hue, hue_range=0.05):
    """restrict a color with 0-1.0 starting hue to hue +/- range. Use this to set reds, blues, etc."""

    # red = 0.0
    # orange = 0.083
    # yellow = 0.17
    # green = 0.29
    # light blue = 0.5
    # dark blue = 0.58
    # blue purple = 0.66
    # purple = 0.79
    # red purple = 0.92

    hue_range = _float_to_byte(min[(hue_range, 0.5)])
    _new_h = (hue - hue_range) + (hsv[0] * 2 * hue_range)
    return _new_h % 255, hsv[1], hsv[2]


def get_ease_in_out_cubic(value):
    """Ease in-out a 0.0 - 1.0 float cubically"""
    # http://gizma.com/easing/
    value *= 2
    if value < 1:
        return 0.5 * value * value * value
    else:
        value -= 2
        return 0.5 * ((value * value * value) + 2)


def get_ease_in_cubic(value):
    """Ease in a 0.0 - 1.0 float cubically"""
    # http://gizma.com/easing/
    return value * value * value


def dim_color(hsv, amount):
    """ dim an hsv color by a 0-1.0 range. 0 == Black; 1 == Full Intensity """
    # using a cubic easing in function
    # http://gizma.com/easing/
    if amount >= 1:
        return hsv
    elif amount <= 0:
        return hsv[0], hsv[1], 0
    else:
        return hsv[0], hsv[1], hsv[2] * get_ease_in_cubic(amount)


def color_to_int(h, s, v):
    """Convert a (byte, byte, byte) color to an int"""
    return int(h) << 16 | int(s) << 8 | int(v)


def int_to_color(color):
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
