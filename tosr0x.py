"""
control wrapper for the TOSR0x USB/WIFI relay board.

The TOSR0x is a relay module based on the FT232RL
chip. This module works with 2-8 relay TOSR0x boards.

For serial/USB, it can discover relay module but currently 
it will only discover a single TOSR0x module
on a given machine. If multiple TOSR0x modules are
required, locations must be explicity specified, e.g.

rm1 = relayModule(devicePath='/dev/ttyUSB3')
rm2 = relayModule(devicePath='/dev/ttyUSB4')

Author: James Stewart
http://jimter.net
http://github/amorphic

Modifications of Jame's library to:

1. Allow control of tosr0x relay modules via WIFI if WIFI module is mounted including LazyBone (module with only 1 relay)
2. Allow to specify number of relays on board to prevent automatic autodetection by toggling all relays which can be harmful depending on what's connected to the relays
3. Allow reading of ambient temperature (for the relay versions that support this option)
4. Consilidate access to relays through low level method send_relay_command()

Author: Alex Roche
http://github.com/alexroche

TODO:
- tidy up args for helper and class
- allow helper to pass relay count
 - separate auto relay count discovery from __set_relay_count__
- fix logging
- proper handling of send_relay_command() to handle it as a crutical section
 - in case this library is called from different threads
- split helper and class into separate modules
- proper docstrings
- add basic command-line tool
"""

import sys
import os
import time
import serial
import types
import socket
import logging
from threading import Lock

# logging
log = logging.getLogger("tosr0x")

# TOSR0x parameters
EXPECTED_MODULE_ID = 15
UNKNOWN_TYPE = 0
SERIAL_TYPE = 1
WIFI_TYPE = 2
MIN_TIME_BETWEEN_COMMANDS = 0.15  # in seconds; 0.15 avoids LazyBone issue
SOCKET_TIMEOUT = 5
SERIAL_DEFAULT_TIMEOUT = 2

# TOSR0x G5LA commands
#  setPosition is in the form: setPosition[position][relay_number]
#  relay_number 0 sets all relays
commands = {
    "getIdVersion": "Z",
    "getStates": "[",
    "getVoltage": "]",
    "getTemperature": "b",
    "setPosition": {
        1: {0: "d", 1: "e", 2: "f", 3: "g", 4: "h", 5: "i", 6: "j", 7: "k", 8: "l"},
        0: {0: "n", 1: "o", 2: "p", 3: "q", 4: "r", 5: "s", 6: "t", 7: "u", 8: "v"},
    },
}


def handler(devicePaths=[], relayCount=None):
    """
    Find attached TOSR0x modules present, intialise and return them in a list.

    :param devicePaths: A device path or list of device paths to scan. If not
        provided, '/dev/ttyUSB[1-255]' will be scanned for compatible devices.
    :type device_paths: :class:`str` or :class:`iterator` of :class:`string`
    :param relayCount: Number of relays present on module (1-8). If not
        provided, all module relays will be cycled to discover this value.
    :type relayCount: :class:`int`
    """
    # Allow a string to be passed for backwards compatibility.
    if isinstance(devicePaths, str):
        devicePaths = [devicePaths]
    if devicePaths == []:
        # Check all device paths /dev/ttyUSB*
        devicePaths = [
            os.path.join("/dev", p) for p in os.listdir("/dev") if "ttyUSB" in p
        ]
    devices = locate_devices(devicePaths, relayCount=relayCount)
    return devices


def locate_devices(devicePaths, relayCount=None):
    """attempt to locate TOSR0x device in a list of device paths"""

    devices = []
    for devicePath in devicePaths:
        device = check_path(devicePath, relayCount=relayCount)
        if device:
            log.info("TOSR0x device found on %s" % devicePath)
            devices.append(device)

    return devices


def check_path(devicePath, relayCount=None):
    """check for TOSR0x device at a given location by querying
    id/verison and checking response"""

    # only continue if path exists
    if not os.path.exists(devicePath):
        return False
    # connect to serial device
    try:
        # usb serial device discovered if no exception thrown
        serialDevice = serial.Serial(devicePath, timeout=SERIAL_DEFAULT_TIMEOUT)
        # read out any existing data
        serialDevice.readall()
    except serial.SerialException as err:
        # location is not a serial device or not behaving as expected
        return False
    log.info("Testing USB serial device on %s" % devicePath)
    # send id/version request
    serialDevice.write(commands["getIdVersion"])
    # module should return 2-byte string indicating module id, software version
    response = convert_hex_to_int(serialDevice.readall())
    if len(response) == 2 and response[0] == EXPECTED_MODULE_ID:
        # expected response returned so device is a TOSR0x
        thisTosr0x = relayModule(serialDevice, relayCount=relayCount)
        return thisTosr0x
    # not expected response so device is not a TOSR0x
    return False


def convert_hex_to_int(hexChars):
    """convert string of hex chars to a list of ints"""

    try:
        ints = [ord(char) for char in hexChars]
        return ints
    except TypeError:
        pass
    return []


def convert_hex_to_bin_str(hexChars):
    """convert hex char into byte string"""

    response = convert_hex_to_int(hexChars)[0]
    # convert int to binary string
    responseBinary = bin(response)
    # first 2 chars of binary string are '0b' so ignore these
    return responseBinary[2:]


class relayModule:
    def __init__(self, device, relayCount=None):
        """initialise relay module"""

        # TOSR0x serial interface or ip address+port

        if type(device) == tuple:
            self.relayAddress = device
            self.type = WIFI_TYPE
        else:
            self.device = device
            self.type = SERIAL_TYPE

        # initialize time of last command
        self.timeOfLastCommand = time.time()

        # set relay count of discovered device
        if relayCount:
            self.relayCount = min(relayCount, 8)
        else:
            if not self.__set_relay_count__():
                log.info("unable to determine number of relays; dafulting to 8")
                self.relayCount = 8

    def __send_relay_command__(self, command, responseRequired=False):
        """send a relay command to the realy considering type of relay
        and returns data returned for rely if responseRequired.
	It returns False in case of error"""

        # treats this method of sending a command and receiving a response as an
        # atomic operation to enable calling it from diferent threads
        # DOESN'T PROTECT IF TWO CLASS INSTANCES ARE USED FOR SAME RELAY MODULE
        criticalSection = Lock()
        with criticalSection:

            # In the case of LazyBone, commands are lost if sent too close
            timeGap = time.time() - self.timeOfLastCommand
            if timeGap < MIN_TIME_BETWEEN_COMMANDS:
                time.sleep(MIN_TIME_BETWEEN_COMMANDS - timeGap)

            correctExecution = True

            if self.type == SERIAL_TYPE:
                try:
                    if self.device.write(command) != 1:
                        log.error("Unexpected Error: Serial Write diff of 1 byte")
                        correctExceution = False
                except:
                    correctExecution = False
                    log.error("error writing to serial device")
                try:
                    if responseRequired:
                        response = self.device.read(16)
                        if len(response) < 1:
                            log.error(
                                "Unexpected Error: Serial Read of less than 1 byte."
                            )
                            correctExecution = False
                except:
                    correctExecution = False
                    log.error("error reading from serial device")

            else:
                # relay type is WIFI_TYPE
                try:
                    # log.info ('Creating socket...')
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.settimeout(SOCKET_TIMEOUT)
                except:
                    correctExecution = False
                    log.error("Unexpected error: socket.socket")
                try:
                    # log.info ('Connecting socket...')
                    self.sock.connect(self.relayAddress)
                except:
                    correctExecution = False
                    log.error("Unexpected error: socket.connect")
                try:
                    # log.info ('Receiving to clear prompt...')
                    self.sock.recv(16)  # clear relay promt
                except:
                    correctExecution = False
                    log.error("Unexpected error: socket.recv(1)")
                try:
                    # log.info ('Sending to socket...')
                    self.sock.sendall(command)
                except:
                    correctExecution = False
                    log.error("Unexpected error: socket.sendall")
                try:
                    if responseRequired:
                        # log.info ('Receiving socket response...')
                        response = self.sock.recv(16)
                except:
                    correctExecution = False
                    log.error("Unexpected error: socket.recv(2)")
                try:
                    # log.info ('Closing socket...')
                    self.sock.shutdown(socket.SHUT_RDWR)
                    self.sock.close()
                except:
                    correctExecution = False
                    log.error("Unexpected error: sock.close")

            self.timeOfLastCommand = time.time()
            if correctExecution and responseRequired:
                return response
            else:
                return correctExecution

    def __set_relay_count__(self):
        """discover count of relays on module by setting all relays
        to position 1 and examining length of status byte
	Retuns False on Error"""

        # set all relays to position 1
        # assuming this command also works for Lazybone although not documented
        if not self.__send_relay_command__(commands["setPosition"][1][0]):
            return False

            # request states from device, read hex response and convert to bin strng
        response = self.__send_relay_command__(commands["getStates"], True)
        if response == False:
            return False

        responseBits = convert_hex_to_bin_str(response)

        self.relayCount = len(responseBits)
        # set all relays to position 0
        if not self.__send_relay_command__(commands["setPosition"][0][0]):
            return False
        return True

    def set_relay_position(self, relay, position):
        """set relay number <relay> to <position> (1 or 0)

        use a <relay> value of 1-8 to set individual relays
        or 0 to set all relays on board"""

        # relay must be an integer 1-8:
        if type(relay) == int and relay in range(0, self.relayCount + 1):
            # position must be an integer 0-1
            if type(position) == int and position in range(0, 2):
                # set relay position
                if self.__send_relay_command__(
                    commands["setPosition"][position][relay]
                ):
                    return True
                else:
                    log.error("error in set_relay_position sending relay command")
            else:
                log.error("position must be 0 or 1")
        else:
            log.error("relay must be 0 (all relays) or 1 - %s", self.relayCount)
        return False

    def get_relay_positions(self):
        """return dictionary of current relay positions or False in case of Error"""

        """the "getStates" command returns a single byte
        representing up to 8 relays. Each bit 1/0 indicates
        the corresponding relay is in position 1/0"""

        # request states from device, read hex response and convert to bin strng
        response = self.__send_relay_command__(commands["getStates"], True)
        if response == False:
            log.error("error in get_relay_positions sending relay command")
            return False
        responseBits = convert_hex_to_bin_str(response)

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

    def get_temperature(self):
        # returns ambient temperature or False in case of error.
        # it should only be called in Relay Module supports it and has a temperature
        # probe connected to it.
        temperature = self.__send_relay_command__(commands["getTemperature"], True)
        if temperature:
            return temperature.rstrip()  # eliminates CR+LF
        else:
            return False
