"""
Model to communicate with a Hex simulator over a TCP socket

"""
import socket
from HelperFunctions import byte_clamp
from color import color_to_int
from hex import HEX_OFFSET


class SimulatorModel(object):
    def __init__(self, hostname, channel, port=4444, debug=False):
        self.server = (hostname, port)
        self.channel = channel  # Which of 2 channels
        self.debug = debug
        self.sock = None
        self.dirty = {}  # { coord: color } map to be sent on the next call to "go"
        self.connect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server)

    def __repr__(self):
        return "Hex Model Channel {} ({}, port={}, debug={})".format(self.channel, self.server[0], self.server[1],
                                                                     self.debug)

    def get_channel(self):
        return self.channel

    # Model basics

    def set_cell(self, cell, color):
        """Set the model's coord to a color"""
        self.dirty[cell] = color

    def go(self):
        """Send all of the buffered commands
           At the very-last minute, an offset needs to be added to the coordinates to keep positive"""
        self.send_start()
        for (coord, color) in self.dirty.items():
            (h, x, y) = coord
            x += HEX_OFFSET
            y += HEX_OFFSET
            hsb_int = color_to_int(byte_clamp(color[0], wrap=True), byte_clamp(color[1]), byte_clamp(color[2]))
            msg = "{}{},{},{},{}".format(self.channel, h, x, y, hsb_int)

            if self.debug:
                print (msg)
            self.sock.send(msg)
            self.sock.send('\n')

        self.dirty = {}  # Restart the dirty dictionary

    def send_start(self):
        """send a start signal"""
        msg = "{}X".format(self.channel)  # tell processing that commands are coming

        if self.debug:
            print (msg)
        self.sock.send(msg)
        self.sock.send('\n')

    def send_delay(self, delay):
        """send a morph amount in milliseconds"""
        msg = "{}D{}".format(self.channel, str(int(delay * 1000)))

        if self.debug:
            print (msg)
        self.sock.send(msg)
        self.sock.send('\n')

    def send_intensity(self, intensity):
        """send an intensity amount (0-255)"""
        msg = "{}I{}".format(self.channel, str(intensity))

        if self.debug:
            print (msg)
        self.sock.send('\n')
        self.sock.send(msg)
        self.sock.send('\n')
