#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''USB serial control wrapper for the TOSR0x USB
relay board.

The TOSR0x is a relay module based on the FT232RL
chip. This module works with 2-8 relay TOSR0x boards.

Will currently only discover a single TOSR0x module
on a given machine. If multiple TOSR0x modules are
required, locations must be explicity specified, e.g.

rm1 = relayModule(devicePath='/dev/ttyUSB3')
rm2 = relayModule(devicePath='/dev/ttyUSB4')

Author: James Stewart
http://jimter.net
http://github/amorphic

TODO:
- fix logging
- proper setup.py etc
- fix pip deployment
- update master with changes here
'''

import sys
import os
import time
import serial
import logging

# logging
log = logging.getLogger('tosr0x')
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

# TOSR0x parameters
expectedModuleId = 15

# TOSR0x G5LA commands
#  setPosition is in the form: setPosition[position][relay_number]
#  relay_number 0 sets all relays
commands = {
    'getIdVersion'  : 'Z',
    'getStates'     : '[',
    'getVoltage'    : ']',
    'setPosition'   : {
        1           : {
            0       : 'd',
            1       : 'e',
            2       : 'f',
            3       : 'g',
            4       : 'h',
            5       : 'i',
            6       : 'j',
            7       : 'k',
            8       : 'l'
        },
        0           : {
            0       : 'n',
            1       : 'o',
            2       : 'p',
            3       : 'q',
            4       : 'r',
            5       : 's',
            6       : 't',
            7       : 'u',
            8       : 'v'
        }
    }
}

def handler(devicePath=False):
    '''find any TOSR0x modules present, intialise and return
    them in a list

    devicePath: eg '/dev/ttyUSB1'. If not provided,
    '/dev/ttyUSB1-255' will be scanned for TOSR0x devices'''

    # create list of device paths to check
    if devicePath:
        # only check device path if provided
        devicePaths = [devicePath]
    else:
        # otherwise check all device paths /dev/ttyUSB*
        devicePaths = [os.path.join('/dev', p) for p in os.listdir('/dev') if 'ttyUSB' in p]
    # attempt to locate TOSR0x devices on paths
    devices = locate_devices(devicePaths)
    return devices

def locate_devices(devicePaths):
    '''attempt to locate TOSR0x device in a list of device paths'''

    devices = []
    for devicePath in devicePaths:
        device = check_path(devicePath)
        if device:
            log.info('TOSR0x device found on %s' % devicePath)
            devices.append(device)

    return devices

def check_path(devicePath):
    '''check for TOSR0x device at a given location by querying
    id/verison and checking response'''

    # only continue if path exists
    if not os.path.exists(devicePath):
        return False
    # connect to serial device
    try:
        # usb serial device discovered if no exception thrown
        serialDevice = serial.Serial(devicePath, timeout=2)
        # read out any existing data
        serialDevice.readall()
    except serial.SerialException, err:
        # location is not a serial device or not behaving as expected
        return False
    log.info('Testing USB serial device on %s' % devicePath)
    # send id/version request
    serialDevice.write(commands['getIdVersion'])
    # module should return 2-byte string indicating module id, software version
    response = convert_hex_to_int(serialDevice.readall())
    if len(response) == 2 and response[0] == expectedModuleId:
        # expected response returned so device is a TOSR0x
        thisTosr0x = relayModule(serialDevice)
        return thisTosr0x
    # not expected response so device is not a TOSR0x
    return False

def convert_hex_to_int(hexChars):
    '''convert string of hex chars to a list of ints'''

    try:
        ints = [ord(char) for char in hexChars]
        return ints
    except TypeError:
        pass
    return []

def convert_hex_to_bin_str(hexChars):
    '''convert hex char into byte string'''

    response = convert_hex_to_int(hexChars)[0]
    # convert int to binary string
    responseBinary = bin(response)
    # first 2 chars of binary string are '0b' so ignore these
    return responseBinary[2:]

class relayModule():

    def __init__(self, serialDevice):
        '''initialise relay module at serialDevie'''

        # TOSR0x serial interface
        self.device = serialDevice
        # set relay count of discovered device
        self.__set_relay_count__()

    def __set_relay_count__(self):
        '''discover count of relays on module by setting all relays
        to position 1 and examining length of status byte'''

        #set all relays to position 1
        self.set_relay_position(0, 1)
        # request states from device
        self.device.write(commands['getStates'])
        # read hex response and convert to binary string
        responseBits = convert_hex_to_bin_str(self.device.readall())
        self.relayCount = len(responseBits)
        #set all relays to position 0
        self.set_relay_position(0, 0)

    def set_relay_position(self, relay, position):
        '''set relay number <relay> to <position> (1 or 0)

        use a <relay> value of 1-8 to set individual relays
        or 0 to set all relays on board'''

        # relay must be an integer 1-8:
        if type(relay) == int and relay in range(0,9):
            # position must be an integer 0-1
            if type(position) == int and position in range(0,2):
                # set relay position
                self.device.write(commands['setPosition'][position][relay])
                return True
            else:
                log.error('position must be 0 or 1')
        else:
            log.error('relay must be 0 (all relays) or 1 - 8')
        return False

    def get_relay_positions(self):
        '''return dictionary of current relay positions'''

        '''the "getStates" command returns a single byte
        representing up to 8 relays. Each bit 1/0 indicates
        the corresponding relay is in position 1/0'''

        # request states from device
        self.device.write(commands['getStates'])
        # read hex response and convert to binary string
        responseBits = convert_hex_to_bin_str(self.device.readall())
        # binary conversion drops values until a 1 is encountered
        # assume missing values are 0 and pad to give a value for all relays
        responseBits = responseBits.zfill(self.relayCount)
        # reverse chars so that relay 1 is first
        responseBits = list(responseBits)
        responseBits.reverse()
        # create dictionary of relay states
        relayStates = {}
        relay = 1
        for bit in responseBits:
            relayStates[relay] = int(bit)
            relay += 1
        return relayStates
