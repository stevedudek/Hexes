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
#  DMX King wiring
#  ---------------
#  GND: Black
#   CK: Green
#   DA: Blue
#   V+: Red
#
#  Dual Shows running that fade into each other
#    Enabled by two instances of the ShowRunner object
#    HexServer's self.channel is now self.channels
#
#  4/20/2020
#
#  Sending singles to the DMX controller
#
#  CLASSES
#
#  ChannelRunner
#  -------------
#  Holds 1 DMX or Processing runner and 1-or-2 HexServers (that each contain their own Hex model with Pixels)
#  Each channel = 1 HexServer
#  ChannelRunner morphs each channel between current and next frames
#  Also interpolate two channels together
#  Sends signals to LEDs via either the DMX or Processing runner
#
#  HexServer
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
#  A Hex model has a dictionary of Pixels = { coord: Pixel object }
#
#  Pixel
#  -----
#  Contain color states (current frame, next frame, interpolation frame)
#  For now, 1 LED per pixel, although code revisions could contain instead an array of LEDs
#  Knows its universe, LED number, and coordinate
#
#  Color
#  -----
#  Not a class, just functional conversions
#  Color is simply a tuple of (hue, saturation, value) with each 0-255
#  Why HSV? Because it makes 2-color interpolation simpler and cleaner (interpolated RGB is muddy)


SHOW_TIME = 30  # Time of shows in seconds
FADE_TIME = 1  # Fade In + Out times in seconds. If FADE_TIME == SHOW_TIME, then "always be fading"
SPEED_MULT = 1  # Multiply every delay by this value. Higher = much slower shows.


class ChannelRunner(object):
    """1. Morph each channel between current and next frames
       2. Interpolate two channels together
       3. send signals to LEDs
       4. Put 2nd channel out of phase with the first and trigger restarting 2nd show"""
    def __init__(self, channels, dmx_runner, has_simulator, max_show_time):
        self.channels = channels  # channels = HexServers
        self.one_channel = (len(self.channels) == 1)  # Boolean
        self.dmx_runner = dmx_runner  # sACN / DMX King
        self.has_simulator = has_simulator
        self.simulator = SimulatorModel(frame_rate=10, hostname="localhost", port=4444) if has_simulator else None
        self.max_show_time = max_show_time
        self.reset_channel_2 = True

    def start(self):
        for channel in self.channels:
            channel.start()  # start related service threads

    def go(self):
        """Run a micro-frame:
           Interpolates all pixels between the hex_model's current color & next frame color as fast as possible
           Interpolation fraction = time.now() between when the last frame finished and the show's yield / delay time
           Fast interpolation turns on LEDs more gradually,
           but may strain the processor
        """
        for channel in self.channels:
            channel.set_interp_frame()  # Set the interp_frames

        if not self.one_channel:
            # ease in-out cubic works; keep it, but does not interact well with dimming
            fract_channel1 = color.get_ease_in_out_cubic(self.channels[0].get_show_intensity())  # 0.0-1.0
            channel1_hex_model, channel2_hex_model = self.channels[0].hex_model, self.channels[1].hex_model

            # Two Channels require channel interpolation
            for coord in channel1_hex_model.all_cells():
                pixel1, pixel2 = channel1_hex_model.get_pixel(coord), channel2_hex_model.get_pixel(coord)
                if pixel1.cell_exists():
                    interp_color = color.interp_color(pixel2.interp_frame, pixel1.interp_frame, fract_channel1)
                    if self.dmx_runner is not None:
                        self.dmx_runner.set(pixel1, interp_color)  # Queue up one pixel's DMX signal
                    if self.simulator:
                        self.simulator.set(pixel1.get_coord(), interp_color)  # Queue up visualizer colors

            self.check_reset_channel_2()  # Force channel 2 to reset if time

        else:
            # One Channel just dumps the single channel
            fract_channel1 = self.channels[0].get_show_intensity()  # 0.0-1.0
            for pixel in self.channels[0].hex_model.all_onscreen_pixels():
                dimmed_interp_color = color.dim_color(pixel.interp_frame, fract_channel1)
                if self.dmx_runner is not None:
                    self.dmx_runner.set(pixel, dimmed_interp_color)  # Queue up one pixel's DMX signal
                if self.simulator:
                    self.simulator.set(pixel.get_coord(), dimmed_interp_color)  # Queue up visualizer colors

        if self.dmx_runner is not None:
            self.dmx_runner.go()  # Dump all DMX signals on to LEDs
        if self.simulator:
            self.simulator.go()  # Try to dump signals to visualizer

    def stop(self):
        for channel in self.channels:
            channel.stop()

    def check_reset_channel_2(self):
        """Check and flip the trigger switch to reset channel 2's show"""
        channel_0_show_fract = self.channels[0].show_runner.show_runtime / self.max_show_time  # 0-2

        if not self.reset_channel_2 and (0.5 <= channel_0_show_fract < 1.0):
            self.channels[1].show_runner.force_next_show()
            self.reset_channel_2 = True

        if self.reset_channel_2 and (1.25 < channel_0_show_fract < 2.0):
            self.reset_channel_2 = False


class HexServer(object):
    """Two channels = two different HexServers
       Mixes a ShowRunner with a Hex model to send show commands on to the hex model
       Holds 1 ShowRunner and 1 Hex model (containing Pixels)"""
    def __init__(self, hex_model, channel, one_channel, max_show_time):
        self.hex_model = hex_model
        self.channel = channel
        self.one_channel = one_channel  # boolean
        self.max_show_time = max_show_time
        self.show_runner = None
        self.running = False
        self._create_services()

    def _create_services(self):
        """Set up the ShowRunners and launch the first shows"""
        self.show_runner = ShowRunner(model=self.hex_model,
                                      channel=self.channel,
                                      one_channel=self.one_channel,
                                      max_show_time=self.max_show_time)

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

    def get_show_intensity(self):
        """Get the channel's intensity from the ShowRunner. Call down."""
        return self.show_runner.get_show_intensity()

    def set_interp_frame(self):
        """Set the ShowRunner's interp_frame. Call down."""
        self.show_runner.set_interp_frame()


class ShowRunner(threading.Thread):
    """Contains 1 Hex model
       Get frames from the Python shows
       Puts those frames on to Hex Model"""
    def __init__(self, model, channel=0, one_channel=True, max_show_time=60):
        super(ShowRunner, self).__init__(name="ShowRunner")
        self.model = model  # Hex class within hex.py
        self.running = True
        self.max_show_time = max_show_time
        self.show_runtime = 0
        self.time_since_reset = 0
        self.external_restart = False  # External trigger to restart show (only for Channel 2)
        self.channel = channel
        self.one_channel = one_channel  # Boolean
        self.num_channels = 1 if one_channel else 2
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
        """Calculates the microframe interpolation fraction (0.0 - 1.0) between frame start time and frame end time"""
        fraction = (datetime.datetime.now() - self.time_frame_start) / (self.time_frame_end - self.time_frame_start)
        fraction = max([min([fraction, 1]), 0])  # Bound fraction between 0-1
        return fraction

    def clear(self):
        self.model.clear()

    def set_interp_frame(self):
        """Set the model's interpolation frame. Call down."""
        self.model.interpolate_frame(self.get_frame_fraction())

    def force_next_show(self):
        """External trigger to queue the next show"""
        self.external_restart = True

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
        self.time_since_reset = 0  # Prevents "bounce" of kicking off many shows
        self.show_runtime = 0
        self.external_restart = False

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
                self.time_frame_start = datetime.datetime.now()  # Set frame's start time as now
                self.time_frame_end = self.time_frame_start + datetime.timedelta(seconds=delay)  # end = now + delay

                time.sleep(delay)  # The only delay! Taken from each show's yield (float) function call.

                self.model.push_next_to_current_frame()  # Get ready for the next frame
                # self.print_heap_size()  # Worried about memory use? Turn this on and check.

                self.show_runtime += delay
                self.time_since_reset += delay

                # Check to see whether to start the next show. The trigger is different for each channel.
                if self.channel == 0:
                    if self.show_runtime >= (self.max_show_time * self.num_channels) and self.time_since_reset > FADE_TIME:
                        print ("max show time elapsed, changing shows")
                        self.next_show()
                else:  # channel 1
                    if self.external_restart and self.time_since_reset > FADE_TIME:
                        print ("external trigger to change shows")
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
        """Return a 0-1 intensity (off -> on) depending on where
           show_runtime is along towards max_show_time"""
        return self.get_one_channel_show_intensity() if self.one_channel else self.get_two_channel_show_intensity()

    def get_two_channel_show_intensity(self):
        """Two-channel shows go to 2 x max_show_time"""
        if self.show_runtime <= FADE_TIME:
            intensity = self.show_runtime / float(FADE_TIME)
        elif self.show_runtime <= self.max_show_time:
            intensity = 1
        elif self.show_runtime <= self.max_show_time + FADE_TIME:
            intensity = 1.0 - ((self.show_runtime - self.max_show_time) / float(FADE_TIME))
        else:
            intensity = 0  # For 2-channel running, the second half of a show's run time will be dark
        return intensity

    def get_one_channel_show_intensity(self):
        """One-channel shows go to 1 x max_show_time"""
        if self.show_runtime <= FADE_TIME:
            intensity = self.show_runtime / float(FADE_TIME)
        elif self.show_runtime >= self.max_show_time - FADE_TIME:
            intensity = (self.max_show_time - self.show_runtime) / float(FADE_TIME)
        else:
            intensity = 1
        return intensity


def get_dmx_runner(bind_address):
    """Turn on the DMX King. Return channels. This will fail if the WiFi is on."""
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


def set_up_channels(num_channels, max_show_time):
    """Get ready for two channels
       Each channel has its own ShowRunner, hex_model, and Pixels"""
    one_channel = (num_channels == 1)  # Boolean
    channels = [HexServer(hex_model=Hex(), channel=channel, one_channel=one_channel, max_show_time=max_show_time)
                for channel in range(num_channels)]
    return channels


if __name__ == '__main__':
    """Main call function for the Hexes"""
    import argparse

    parser = argparse.ArgumentParser(description='Hexes Light Control')
    parser.add_argument('--max_time', action='store_true', default=int(SHOW_TIME),
                        help='Maximum number of seconds a show will run (default {})'.format(SHOW_TIME))
    parser.add_argument('--list', action='store_true', help='List available shows')
    parser.add_argument('--bind', help='Local address to use for sACN')
    parser.add_argument('--simulator', action='store_true', default=False, help='use the processing simulator')
    parser.add_argument('--dmxoff', action='store_true', default=False, help='turn off the DMX controller')
    parser.add_argument('--onechannel', action='store_true', default=False, help='remove dual shows')
    parser.add_argument('shows', metavar='show_name', type=str, nargs='*',
                        help='name of show (or shows) to run')

    args = parser.parse_args()

    if args.list:
        print ("Available shows:")
        print (', '.join([show[0] for show in shows.load_shows(channel=None, path=None)]))
        sys.exit(0)

    if args.onechannel:
        num_channels = 1
        FADE_TIME = max([FADE_TIME, SHOW_TIME / 2.0])
    else:
        num_channels = 2

    dmx_runner = get_dmx_runner(args.bind) if not args.dmxoff else None

    channel_runner = ChannelRunner(channels=set_up_channels(num_channels, args.max_time), dmx_runner=dmx_runner,
                                   has_simulator=args.simulator, max_show_time = args.max_time)
    channel_runner.start()

    try:
        while True:
            channel_runner.go()

    except KeyboardInterrupt:
        print ("Exiting on keyboard interrupt")

    finally:
        channel_runner.stop()

