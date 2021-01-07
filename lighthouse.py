#!/usr/bin/env python3

import asyncio
import os
import re
import sys
from abc import ABC
from bleak import discover, BleakClient
from output import output

class Lighthouse(ABC):
    """The abstract base for the physical Lighthouse devices.

    Attributes
    ----------
    lighthouse_type : int
        The version of SteamVR lighthouse to search for, 1 or 2
    name_prefix : string
        The prefix to the name of the Bluetooth device
    service : string
        The UUID of the GATT service for lighthouse management
    characteristic_values : dict
        A dictionary of bytearrays containing valid power management commands
    characteristic_states : dict
        A dictionary of bytearrays containing potential power management states
    """

    lighthouse_type = None
    name_prefix = ""
    service = ""
    characteristic = ""
    characteristic_values = {}
    characteristic_states = {}

    def __init__(self, mac):
        if not re.match("[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}", mac):
            sys.exit("MAC address '" + mac + "' is not valid.")

        self.mac = mac

    async def run_command(self, loop, command, retries = 10):
        """Write a command to the Lighthouse Bluetooth device.

        The command references a value in `characteristic_values` to be
        written to the GATT characteristic specified by `characteristic`.

        Parameters
        ----------
        loop : AbstractEventLoop
            The asyncio event loop
        command : str
            The command to write to the lighthouse
        retries : int, optional
            Max number of times to retry writing to the lighthouse
        """

        if command not in self.characteristic_values:
            sys.exit("Command '" + command + "' is not valid.")

        success = False

        for attempt in range(retries):
            if attempt == 0:
                output.info(self.mac + ": attempting to switch " + command)
            else:
                output.info(self.mac + ": retrying command, attempt #" + str(attempt + 1))

            client = BleakClient(self.mac, loop=loop)

            try:
                await client.connect()

                state = await client.read_gatt_char(self.characteristic)

                if command == "off" and state in self.characteristic_states["off"]:
                    output.info(self.mac + ": is already off, skipping")
                    success = True
                    break

                await client.write_gatt_char(self.characteristic, self.characteristic_values[command])

                if command == "on":
                    output.info(self.mac + ": switched on")
                if command == "off" and self.lighthouse_type == 1:
                    output.info(self.mac + ": will enter standby in one minute")
                if command == "off" and self.lighthouse_type == 2:
                    output.info(self.mac + ": switched off")

                success = True
                break
            except Exception as e:
                output.exception(str(e))
            finally:
                try:
                    await client.disconnect()
                except Exception as e:
                    output.exception(str(e))

        if not success:
            output.info(self.mac + ": reached max attempts ({}).".format(retries))

class LighthouseV1(Lighthouse):
    lighthouse_type = 1
    name_prefix = "HTC BS"
    service = "0000cb00-0000-1000-8000-00805f9b34fb"
    characteristic = "0000cb01-0000-1000-8000-00805f9b34fb"

    characteristic_values = {
        "on": bytearray.fromhex("12001202ffffffff000000000000000000000000"),
        "off": bytearray.fromhex("12010004ffffffff000000000000000000000000"),
    }

    characteristic_states = {
        "on": [bytearray.fromhex("0012000000000000000000000000000000000000")],
        "off": [bytearray.fromhex("0012003c00000000000000000000000000000000")],
    }

class LighthouseV2(Lighthouse):
    lighthouse_type = 2
    name_prefix = "LHB-"
    service = "00001523-1212-efde-1523-785feabcd124"
    characteristic = "00001525-1212-efde-1523-785feabcd124"

    characteristic_values = {
        "on": bytearray([0x01]),
        "off": bytearray([0x00])
    }

    characteristic_states = {
        "on": [bytearray([0x01]), bytearray([0x09]), bytearray([0x0b])],
        "off": [bytearray([0x00])],
    }
