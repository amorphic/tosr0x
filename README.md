TOSR0x
======================

A Python module for communicating with 'TOSR0x' relay controllers available at [tinyosshop.com](http://www.tinyosshop.com/index.php?route=product/product&product_id=365) and other online retailers.

*Note: as of v0.6.0 this module only supports Python 3.4+.*

Supported Hardware
----------------------

* [TOSR0x USB 2-8 relay](http://www.tinyosshop.com/index.php?route=product/category&path=141_142)
* [TOSR0x WiFi 2-8 relay](http://www.tinyosshop.com/index.php?route=product/category&path=141_143)
* [LazyBone WiFi single relay](http://www.tinyosshop.com/index.php?route=product/category&path=141_129)

Functionality
----------------------

* Detect TOSR0x USB and WiFi devices.
* Set relay states.
* Query relay states.
* Query temperature (on supported models).

Requirements
----------------------

* Python serial module (should be installed by default)

Installation
----------------------

Use setup.py:

    python setup.py install

If using Debian or a derivative (Ubuntu) additional USB permissions may be required:

 Add the user to the 'dialout' group:

    $ sudo usermod -G dialout -a <username>

 Add a udev rules file to allow access to usb devices:

    $ cat /etc/udev/rules.d/50-usb.rules
    # allow access to usb devices for users in dialout group
    SUBSYSTEM=="usb", MODE="0666", GROUP="dialout"

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

By default the handler scans all USB ports for compatible tosr0x devices. You
can also specify a range of ports to scan:

    >th = tosr0x.handler(devicePath=['/dev/ttyUSB3'])

    Testing USB serial device on /dev/ttyUSB3
    TOSR0x device found on /dev/ttyUSB3

Usually all relays on the module are cycled at initialisation to determine the
relay count. You can specify a relay count to prevent this:

    >th = tosr0x.handler(devicePath=['/dev/ttyUSB3'], relayCount=4)

    Testing USB serial device on /dev/ttyUSB3
    TOSR0x device found on /dev/ttyUSB3

It is also possible to use the class directly without using the handler:

    FOR SERIAL:
    >import serial
    >import tosr0x
    >sd=serial.Serial('/dev/ttyUSB0', timeout=0.1)
    >myTosr0x=tosr0x.relayModule(sd) #Num relays not specified in this example

    FOR WIFI:
    >import tosr0x
    >myTosr0x = tosr0x.relayModule( ('192.168.1.2',2000), 2) #Module of 2 relays

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

* James Stewart (@amorphic) uses to _tosr0x_ to implement an Environmental Controller in [braubuddy](http://braubuddy.org), a temperature monitoring framework.
* Alex Roche (@alexroche) is using _tosr0x_ with WIFI option to control blinds through openremote controller running on a Raspberry Pi.
