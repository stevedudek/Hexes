#!/usr/bin/env python3.7
import datetime
import netifaces
import sys
import time
import traceback
import threading

import color as color
from hex import Hex, NUM_HEXES
import shows

from model.sacn_model import sACN  # Sends signals to DMX King
from model.simulator import SimulatorModel  # Sends signals to Processing screen

#
#  Dual Shows running that fade into each other
#    Enabled by two instances of the ShowRunner object
#    HexServer's self.channel is now self.channels
#
#  4/19/2020
#
#  Sending singles to the DMX controller
#
#  CLASSES
#
#  ChannelRunner
#  -------------
#  Holds 1 DMX or Processing runner and 1-or-2 HexServers (that contain Hex models with Pixels)
#  Each channel = 1 HexServer
#  ChannelRunner morphs each channel between current and next frames
#  Interpolate two channels together
#  Sends signals to LEDs via either the DMX or Processing runner
#
#  HexServer (ToDo: should HexServer get consolidated with the the ShowRunner?)
#  ---------
#  Mixes a ShowRunner and a Hex model to send show commands on to the hex model
#  Holds 1 ShowRunner and 1 Hex model (containing Pixels)
#
#  ShowRunner
#  ----------
#  Contains 1 Hex model
#  Get frames from the Python shows
#  Puts those frames on to Hex Model
#
#  Hex model
#  ---------
#  Dictionary of {coord: pixel}
#  Ability to set a pixel's color, clear all pixels, etc.
#  Each channel should have its own Hex model


NUM_CHANNELS = 1  # Dual channels
SHOW_TIME = 160  # Time of shows in seconds
FADE_TIME = 20  # Fade In + Out times in seconds
SPEED_MULT = 1  # Multiply every delay by this value. Higher = much slower shows


class ChannelRunner(object):
    """1. Morph each channel between current and next frames
       2. Interpolate two channels together
       2. send signals to LEDs"""
    def __init__(self, channels, dmx_runner):
        self.channels = channels  # channels = HexServers
        self.dmx_runner = dmx_runner  # sACN or to-Processing model
        self.running = True

    def start(self):
        for channel in self.channels:
            channel.start()  # start related service threads

    def go(self):
        """Run a microframe"""
        for channel in self.channels:
            channel.set_interp_frame()  # Set the interp_frames

        if len(self.channels) == 2:
            channel1_hex_model, channel2_hex_model = self.channels[0].hex_model, self.channels[1].hex_model
            fract_channel1 = self.channels[0].get_intensity()
            print(fract_channel1)

            # Two Channels require channel interpolation
            for coord in channel1_hex_model.all_cells():
                pixel1, pixel2 = channel1_hex_model.get_pixel(coord), channel2_hex_model.get_pixel(coord)
                if pixel1.cell_exists():
                    interp_color = color.interp_color(pixel1.interp_frame, pixel2.interp_frame, fract_channel1)
                    dmx_runner.set(pixel1, interp_color)  # Queue up one pixel's DMX signal

        else:
            # One Channel just dumps the single channel
            for pixel in self.channels[0].hex_model.all_onscreen_pixels():
                dmx_runner.set(pixel, pixel.interp_frame)  # Queue up one pixel's DMX signal

        dmx_runner.go()  # Dump all DMX signals on to LEDs

    def stop(self):
        for channel in self.channels:
            channel.stop()

    def stagger_channels(self):
        if len(self.channels) > 1:
            self.channels[1].show_runner.show_runtime = (self.channels[0].show_runner.show_runtime + (SHOW_TIME / 2.0)) % SHOW_TIME


class HexServer(object):
    def __init__(self, hex_model, channel):
        self.hex_model = hex_model
        self.channel = channel
        self.args = args
        self.show_runner = None
        self.running = False
        self._create_services()

    def _create_services(self):
        """Set up the ShowRunners and launch the first shows"""
        self.show_runner = ShowRunner(model=self.hex_model,
                                      max_showtime=args.max_time,
                                      channel=self.channel)

        if args.shows:
            named_show = args.shows[0]
            print("setting show: ".format(named_show))
            self.show_runner.next_show(named_show)

    def start(self):
        try:
            self.show_runner.start()
            self.running = True
        except Exception as e:
            print("Exception starting Hexes!")
            traceback.print_exc()

    def stop(self):
        if self.running:  # should be safe to call multiple times
            try:
                self.running = False
                self.show_runner.stop()
            except Exception as e:
                print("Exception stopping Hexes! {}".format(e))
                traceback.print_exc()

    def get_intensity(self):
        """Get the channel's intensity from the ShowRunner"""
        return self.show_runner.show_intensity

    def set_interp_frame(self):
        """Set the ShowRunner's interp_frame"""
        self.show_runner.set_interp_frame()


class ShowRunner(threading.Thread):
    def __init__(self, model, max_showtime=1000, channel=0):
        super(ShowRunner, self).__init__(name="ShowRunner")
        self.model = model  # Hex class within hex.py
        self.running = True
        self.max_show_time = max_showtime
        self.show_runtime = 0
        self.show_intensity = 0
        self.time_since_reset = 0
        self.channel = channel
        # self.lock = threading.Lock()  # Prevent overlapping messages
        self.time_frame_start = datetime.datetime.now()
        self.time_frame_end = datetime.datetime.now()

        # map of names -> show constructors
        self.shows = dict(shows.load_shows())
        self.randseq = shows.random_shows()

        # current show object & frame generator
        self.show = None
        self.framegen = None
        self.prev_show = None
        self.show_params = None

    def get_frame_fraction(self):
        fraction = (datetime.datetime.now() - self.time_frame_start) / (self.time_frame_end - self.time_frame_start)
        fraction = max([min([fraction, 1]), 0])  # Bound fraction between 0-1
        return fraction

    def clear(self):
        self.model.clear()

    def set_interp_frame(self):
        """Set the model's interpolation frame"""
        self.model.interpolate_frame(self.get_frame_fraction())

    def next_show(self, name=None):
        show = None
        if name:
            if name in self.shows:
                show = self.shows[name]
            else:
                print ("unknown show: {}".format(name))

        if not show:
            print ("choosing random show")
            show = next(self.randseq)

        self.clear()
        self.prev_show = self.show
        self.show = show(self.model)  # Calls the particular show.__init__(hex_model)
        self.framegen = self.show.next_frame()
        self.show_params = hasattr(self.show, 'set_param')
        self.time_since_reset = 0
        if self.channel == 0:
            self.show_runtime = 0  # Don't reset other channels' clocks

        print ("next show for channel {}: {}".format(self.channel, self.show.name))

    def get_next_frame(self):
        """return a delay or None"""
        try:
            return next(self.framegen)
        except StopIteration:
            return None

    def run(self):
        if not (self.show and self.framegen):
            self.next_show()

        while self.running:
            try:
                # Run a single frame of a show
                delay = self.get_next_frame() * SPEED_MULT  # float seconds
                self.time_frame_start = datetime.datetime.now()
                self.time_frame_end = self.time_frame_start + datetime.timedelta(seconds=delay)
                self.show_intensity = self.get_show_intensity()  # Calculate the channel strength (0-1)

                time.sleep(delay)  # The only delay!

                self.model.push_next_to_current_frame()  # Get ready for the next fream
                # self.print_heap_size()

                if self.show_runtime >= self.max_show_time and self.time_since_reset > FADE_TIME:
                    print ("max show time elapsed, changing shows")
                    self.next_show()

            except Exception:
                print ("unexpected exception in show loop!")
                traceback.print_exc()
                self.next_show()

    @staticmethod
    def print_heap_size():
        """print python heap size - useful for debugging"""
        import resource
        megabytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000
        if megabytes > 30:
            print("Using: {}Mb".format(megabytes))

    def stop(self):
        self.running = False

    def get_show_intensity(self):
        """Return a 0-255 intensity (off -> on) depending on where
           show_runtime is along towards max_show_time"""
        if self.show_runtime <= FADE_TIME:
            intensity = 255 * self.show_runtime / FADE_TIME
        elif self.show_runtime <= self.max_show_time / 2.0:
            intensity = 255
        elif self.show_runtime <= (self.max_show_time / 2.0) + FADE_TIME:
            intensity = 255 * (FADE_TIME - (self.show_runtime - (self.max_show_time / 2.0))) / FADE_TIME
        else:
            intensity = 0
        return int(round(intensity))

#
# def turn_on_simulator():
#     """Turn on the Processing simulator. Return channels"""
#     sim_host = "localhost"
#     sim_port = 4444  # base port number
#
#     print ("Using Hex Simulator at {}:{}-{}".format(sim_host, sim_port, sim_port + NUM_CHANNELS - 1))
#
#     # ToDo: This is going to change
#     # ToDo: Processing will not handle the dual shows
#     # ToDo: Dual shows will be handles in go_dmx with model interpolation
#
#
#     # Get ready for DUAL channels
#     # Each channel (app) has its own ShowRunner and SimulatorModel
#     channels = []  # array of channel objects
#     for channel in range(NUM_CHANNELS):
#         hex_simulator = SimulatorModel(sim_host, i, port=sim_port + i)
#         hex_model = hex.load_hexes(hex_simulator)
#         channels.append(HexServer(hex_model=hex_model, hex_simulator=hex_simulator, channel=args))
#     return channels


def get_dmx_runner(bind_address):
    """Turn on the DMX King. Return channels"""
    if not bind_address:
        gateways = netifaces.gateways()[netifaces.AF_INET]

        for _, interface, _ in gateways:
            for address in netifaces.ifaddresses(interface).get(netifaces.AF_INET, []):
                if address['addr'].startswith('192.168.0'):
                    print("Auto-detected DMX King local IP: {}".format(address['addr']))
                    bind_address = address['addr']
                    break
            if bind_address:
                break

        if not bind_address:
            print("Failed to auto-detect local DMX King IP")

    print("Starting sACN")

    dmx_runner = sACN(bind_address=bind_address, num_hexes=NUM_HEXES)
    dmx_runner.activate()
    return dmx_runner


def set_up_channels():
    # Get ready for DUAL channels
    # Each channel (app) has its own ShowRunner, hex_model, and Pixels
    channels = [HexServer(hex_model=Hex(), channel=channel) for channel in range(NUM_CHANNELS)]
    return channels


if __name__ == '__main__':
    """Main call function for the Hexes"""
    import argparse

    parser = argparse.ArgumentParser(description='Hexes Light Control')
    parser.add_argument('--max-time', type=float, default=float(SHOW_TIME),
                        help='Maximum number of seconds a show will run (default {})'.format(SHOW_TIME))
    parser.add_argument('--list', action='store_true', help='List available shows')
    parser.add_argument('--bind', help='Local address to use for sACN')
    parser.add_argument('--simulator', action='store_true', default=False, help='use the processing simulator')
    parser.add_argument('shows', metavar='show_name', type=str, nargs='*',
                        help='name of show (or shows) to run')

    args = parser.parse_args()

    if args.list:
        print ("Available shows:")
        print (', '.join([show[0] for show in shows.load_shows()]))
        sys.exit(0)

    if args.simulator:
        dmx_runner = None
    else:
        dmx_runner = get_dmx_runner(args.bind)

    channel_runner = ChannelRunner(channels=set_up_channels(), dmx_runner=dmx_runner)
    channel_runner.start()

    try:
        while True:
            channel_runner.stagger_channels()  # Force channel 1 out of phase with channel 2 by 50%
            channel_runner.go()

    except KeyboardInterrupt:
        print ("Exiting on keyboard interrupt")

    finally:
        channel_runner.stop()

