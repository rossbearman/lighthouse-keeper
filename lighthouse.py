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
    lighthouseType : int
        The version of SteamVR lighthouse to search for, 1 or 2
    namePrefix : string
        The prefix to the name of the Bluetooth device
    service : string
        The UUID of the GATT service for lighthouse management
    characteristicValues : string
        A dictionary of bytearrays containing valid power management commands
    characteristicStates : string
        A dictionary of bytearrays containing potential power management states
    """

    lighthouseType = None
    namePrefix = ""
    service = ""
    characteristic = ""
    characteristicValues = {}
    characteristicStates = {}

    def __init__(self, mac):
        if not re.match("[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}", mac):
            sys.exit("MAC address '" + mac + "' is not valid.")

        self.mac = mac

    async def runCommand(self, loop, command, retries = 10):
        """Write a command to the Lighthouse Bluetooth device.

        The command references a value in `characteristicValues` to be
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

        if command not in self.characteristicValues:
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

                if command == "off" and state in self.characteristicStates["off"]:
                    output.info(self.mac + ": is already off, skipping")
                    success = True
                    break

                await client.write_gatt_char(self.characteristic, self.characteristicValues[command])

                if command == "on":
                    output.info(self.mac + ": switched on")
                if command == "off" and self.lighthouseType == 1:
                    output.info(self.mac + ": will enter standby in one minute")
                if command == "off" and self.lighthouseType == 2:
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
    lighthouseType = 1
    namePrefix = "HTC BS"
    service = "0000cb00-0000-1000-8000-00805f9b34fb"
    characteristic = "0000cb01-0000-1000-8000-00805f9b34fb"

    characteristicValues = {
        "on": bytearray.fromhex("12001202ffffffff000000000000000000000000"),
        "off": bytearray.fromhex("12010004ffffffff000000000000000000000000"),
    }

    characteristicStates = {
        "on": [bytearray.fromhex("0012000000000000000000000000000000000000")],
        "off": [bytearray.fromhex("0012003c00000000000000000000000000000000")],
    }

class LighthouseV2(Lighthouse):
    lighthouseType = 2
    namePrefix = "LHB-"
    service = "00001523-1212-efde-1523-785feabcd124"
    characteristic = "00001525-1212-efde-1523-785feabcd124"

    characteristicValues = {
        "on": bytearray([0x01]),
        "off": bytearray([0x00])
    }

    characteristicStates = {
        "on": [bytearray([0x01]), bytearray([0x09]), bytearray([0x0b])],
        "off": [bytearray([0x00])],
    }
