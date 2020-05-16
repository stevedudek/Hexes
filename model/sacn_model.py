"""
sACN: Class to communicate with the DMX King (should only be 1 instance)
"""
import sacn  # Must use Python >= 3.6
import color as color_func


class sACN(object):
    def __init__(self, bind_address, num_hexes, brightness=1.0):
        self.num_hexes = num_hexes
        self.brightness = brightness
        self.sender = sacn.sACNsender(
            bind_address=bind_address,
            universeDiscovery=True,
        )
        self.leds = {}  # { h: 512 ints (3 for each LED) }

    def activate(self):
        self.sender.start()
 
        # leds is a dictionary that holds 512 ints for each Hex number
        # conceivably can support 170 LEDS per display
        for h in range(1, self.num_hexes + 1):  # universes are 1-indexed
            self.leds[h] = [0] * 512
            self.sender.activate_output(h)
            self.sender[h].multicast = True
            print('Activating sACN universe {} ({} channels)'.format(h, len(self.leds[h])))

    def stop(self):
        for universe_index in self.leds:
            self.sender.deactivate_output(universe_index)
        self.sender.stop()

    def __del__(self):
        self.stop()

    def set(self, pixel, color):
        universe, index = pixel.get_universe_index()
        try:
            _ = self.leds[universe]
        except KeyError:
            raise IndexError("Channel {} does not exists".format(universe))

        # Dim hsv and convert hsv to rgb
        if self.brightness < 1:
            color = color_func.dim_color(color, amount=self.brightness)

        for i, c in enumerate(color_func.hsv_to_rgb(color)):
            try:
                self.leds[universe][index + i] = c
            except IndexError:
                raise IndexError("Universe: {}, Index: {} does not exist".format(universe, index))

    def go(self):
        for universe_index in self.leds:
            self.sender[universe_index].dmx_data = self.leds[universe_index]
