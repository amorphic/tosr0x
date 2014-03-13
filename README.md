tosr0x
======================

A Python module for communicating with 'TOSR0x' USB relay controllers available at [tinyosshop.com](http://www.tinyosshop.com/index.php?route=product/product&product_id=365) and other online retailers.

The module is a wrapper around Python's default serial module. It provides functionality to detect TOSR0x devices, set relay states and query relay states.

Modifications by Alex from the original library:
-----------------------------------------------

The automatic discovery of number of relays is made optional, for the cases when it is not acceptable to toggle relay status as a method for discovering relays.If a number of relays is specified when an instance is created, then the intrusive automatic discovery won't be executed. 

These modules can also mount a WIFI card. This library now supports connecting to the relay modules either through serial interface or WIFI.  For a WIFI relay you can cerate a instance indicating IP address, port and optionally the relay count of this module (1 for Lazybone, 2, 4 or 8)

   e.g. myTosr0x = tosr0x.relayModule('192.168.1.2',2000),2)

There are some newer modules from tinyos that have the option to attach a temperature probe, and in this case it is possible to read the temperature through an additional command. For this case, a new 'get_temperature' method is added to read the ambient temperature.

It's pending to handle some error conditions.

Requirements
----------------------

* A TOSR0x USB relay controller, (2-relay model tested but should work with 2:8-relay models)
* Linux (may work with other Unix variants)
* Python serial module (should be installed by default)

Installation
----------------------

Use setup.py:

    python setup.py install

If using Debian or a derivative (Ubuntu) additional USB permissions may be required:

 Add the user to the 'dialout' group:

    >sudo usermod -G dialout -a <username>

 Add a udev rules file to allow access to usb devices:

    >cat /etc/udev/rules.d/50-usb.rules
    # allow access to usb devices for users in dialout group
    'SUBSYSTEM=="usb", MODE="0666", GROUP="dialout"

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

It is possible to use directly the class without using the handler:

    >import serial
    >sd=serial.Serial('/dev/ttyUSB0', timeout=2)
    >myTosr0x=tosr0x.relayModule(sd) 

Set relay states to either 0 or 1:

    >myTosr0x.set_relay_position(1,1)
    True

    >myTosr0x.set_relay_position(2,0)
    True

(Note: relay numbering starts at 1. Set the state of all relays by using relay number 0.)

Get relay positions, (returned as a dict {relay : state}):

    >myTosr0x.get_relay_positions()
    {1: 1, 2: 0}

Get Ambient Temperaure n Celsius degree for modules supporting a temperature probe:

    >myTosr0x.get_temperature()
    23.94

Projects
----------------------

This module will form the basis of my forthcoming thermostat framework, [braubuddy](https://github.com/amorphic/braubuddy).

Alex is using a relay module with WIFI option to control blinds through openremote controller running on a raspberry pi.
