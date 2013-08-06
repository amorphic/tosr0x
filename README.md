tosr0x
======================

A Python module for communicating with 'TOSR0x' USB relay controllers available at [tinyosshop.com](http://www.tinyosshop.com/index.php?route=product/product&product_id=365) and other online retailers.

The module is a wrapper around Python's default serial module. It provides functionality to detect TOSR0x devices, set relay states and query relay states.


Requirements
----------------------

* A TOSR0x USB relay controller, (2-relay model tested but should work with 2:8-relay models)
* Linux (may work with other Unix variants)
* Python serial module (should be installed by default)

Usage
----------------------

Call the handler function to return a list of tosr0x objects:

    >import tosr0x
    >th = tosr0x.handler()

    Testing USB serial device on /dev/ttyUSB0
    Testing USB serial device on /dev/ttyUSB1
    Testing USB serial device on /dev/ttyUSB2
    Testing USB serial device on /dev/ttyUSB3
    TOSR0x device found on /dev/ttyUSB3

    >myTosr0x = th[0]
    >print myT0sr0x

    <tosr0x.relayModule instance at 0xb68be46c>

Alternatively, specify a USB serial device: 

    >th = tosr0x.handler('/dev/ttyUSB3')

    Testing USB serial device on /dev/ttyUSB3
    TOSR0x device found on /dev/ttyUSB3

Set relay states to either 0 or 1:

    >myTosr0x.set_relay_position(1,1)
    True

    >myTosr0x.set_relay_position(2,0)
    True

(Note: relay numbering starts at 1. Set the state of all relays by using relay number 0)

Get relay positions, (returned as a dict {relay : state}):

    >myTosr0x.get_relay_positions()
    {1: 1, 2: 0}

Projects
----------------------

This module will form the basis of my forthcoming Python-based temperature controller, [braubuddy](https://github.com/jstewart101/braubuddy).

If you use this module in an interesting project please let me know and I'll add a link here.
