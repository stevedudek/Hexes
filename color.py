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
    """Interpolate between hsv1 and hsv2"""
    if fraction <= 0:
        return hsv1
    elif fraction >= 1:
        return hsv2
    # elif not are_different(hsv1, hsv2):
    #     return hsv1
    elif hsv1[2] == 0:  # 1 is black, so dim 2
        return dim_color(hsv2, fraction)
    elif hsv2[2] == 0:  # 2 is black, so dim 1
        return dim_color(hsv1, 1 - fraction)
    else:
        return interp_value(hsv1[0], hsv2[0], fraction), \
               interp_value(hsv1[1], hsv2[1], fraction), \
               interp_value(hsv1[2], hsv2[2], fraction),


def interp_value(v1, v2, fraction):
    return int(v1 + (fraction * (v2 - v1)))


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


def dim_color(hsv, amount):
    """dim an hsv color by a 0-1.0 range"""
    dim_amount = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
                  1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7, 8,
                  8, 8, 9, 9, 9, 10, 10, 11, 11, 12, 12, 12, 13, 13, 14, 14, 15, 15, 16, 16, 17,
                  17, 18, 18, 19, 19, 20, 21, 21, 22, 22, 23, 24, 24, 25, 25, 26, 27, 27, 28, 29,
                  29, 30, 31, 31, 32, 33, 34, 34, 35, 36, 37, 37, 38, 39, 40, 41, 41, 42, 43, 44,
                  45, 45, 46, 47, 48, 49, 50, 51, 52, 53, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62,
                  63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 76, 77, 78, 79, 80, 81, 82, 83,
                  84, 86, 87, 88, 89, 90, 92, 93, 94, 95, 96, 98, 99, 100, 101, 103, 104, 105, 106,
                  108, 109, 110, 112, 113, 114, 116, 117, 118, 120, 121, 123, 124, 125, 127, 128,
                  130, 131, 132, 134, 135, 137, 138, 140, 141, 143, 144, 146, 147, 149, 150, 152,
                  153, 155, 157, 158, 160, 161, 163, 164, 166, 168, 169, 171, 173, 174, 176, 178,
                  179, 181, 183, 184, 186, 188, 189, 191, 193, 195, 196, 198, 200, 202, 203, 205,
                  207, 209, 211, 212, 214, 216, 218, 220, 222, 224, 225, 227, 229, 231, 233, 235,
                  237, 239, 241, 243, 245, 247, 249, 251, 253, 255]

    if amount >= 1:
        return hsv
    elif amount <= 0:
        return hsv[0], hsv[1], 0
    else:
        return hsv[0], hsv[1], dim_amount[min([int(hsv[2] * amount), 255])]  # > 255 crashes the above array


def color_to_int(h, s, v):
    """Convert a (byte, byte, byte) color to an int"""
    return int(h) << 16 | int(s) << 8 | int(v)


def int_to_color(color):
    return (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
