## Hexes README

### Contents

1. Overview
2. How to Use
2. Goals
3. The Bad
4. The Good
5. Next step

### Overview

This Hex Repository controls 1-4 panels of 109 wd2801 RGB LEDs via a DMX King
For viewing at home, the user can turn on a Processing visualizer.

### How to use

One DMX King connects to 1-4 Hex panels.
Either a laptop or Raspberry Pi (not tested yet) connects to the DMX King via internet.

clone the repository:

```
git clone https://github.com/stevedudek/Hexes.git
```

set up the pyramidtriangles *ve* with Python 3.6+

```
./go_dmx.py --bind 192.168.0.119  # run Hex code to the DMX King
./go_dmx.py --simulator --bind 192.168.0.119  # turn on simulator and DMX King
./go_dmx.py --simulator --dmxoff  # run only the Processing simulator
./go_dmx.py --simulator --dmxoff --onechannel  # turn off dual channels
```

The Processing simulator, **HexSimulatorOnly**, runs with either Processing 2 or 3 (you will need to change one code line)

### Goals

#### The Problem

For about a decade, I've invested in an LED technology stack of
* LEDs
* Pixel Pusher Hardware
* Processing software and visualizer
* Python show runner
* Laptop

The Pixel Pusher robustly handles power distribution, but currently the Pixel Pusher depends on Processing to send it LED signals.
Not only is Processing potentially slow (limited to 30-50 frames per second),
but also I'm having trouble installing Processing on a Raspberry Pi, requiring a laptop instead.
A DMX King (thanks, John Major) may free up this technological barrier.

#### Initial Goals

0. Rip out most of the Pyramid Triangles code, so I can understand the simplest pieces
1. Get the DMX King to talk to a new (actually old) type of LED: RGB ws2801
2. Get previously-written Python LED shows to work with the DMX King
3. Add a few LED features: frame interpolation, dual-show running
4. Bring back an optional Processing visualizer for debugging and LED-free running

#### The Bad

* This Hex repository is not written (yet) for the Pyramid's Triangles
* Much of the Pyramid functionality is gone: flexible LED/strip mapping, Cherry Pi, abstract classes
* You may find such stripped-down limitations aggravating

#### The Good

* The code base is a lot simpler for me to build back in functionality
* Supports **frame interpolation**: for example, if a LED show yields for 1 second, the ChannelRunner within *go_dmx.py* knows to interpolate all LEDs at ~60 fps.
* Supports **dual channels**: the code natively runs two random shows at once, staggered, blending them together,

#### Next Steps

* Most of the Hex shows are too complicated and so blend poorly with other complex shows, so
* Write simpler Hex shows. This is a good problem to have.
* Work with John and Justin to port this simplified DMX code back into the Pyramid Triangles code base







