#!/usr/bin/env python3

import asyncio
import os
import re
import sys
from lighthouse import LighthouseV1, LighthouseV2
from bleak import discover, BleakClient
from output import output

class LighthouseLocator():
    """Discover lighthouses in the local environment via Bluetooth

    Attributes
    ----------
    lighthouseType : int
        The version of SteamVR lighthouse to search for, 1 or 2
    """

    def __init__(self, lighthouseType):
        self.lighthouseType = lighthouseType

        if lighthouseType == 1:
            self.namePrefix = LighthouseV1.namePrefix
            self.serviceId = LighthouseV1.service
            self.characteristicId = LighthouseV1.characteristic
        else:
            self.namePrefix = LighthouseV2.namePrefix
            self.serviceId = LighthouseV2.service
            self.characteristicId = LighthouseV2.characteristic

    async def discover(self):
        lighthouses = []
        devices = await discover()
        for device in devices:
            isLighthouse = False

            if device.name.find(self.namePrefix) != 0:
                continue

            # TODO: Verbose - potential lighthouse found
            output.debug("Found potential lighthouse '" + device.name + "' identified by '" + device.address + "'")
            output.debug(device.address + " signal strength: " + str(device.rssi))
            services = None

            async with BleakClient(device.address) as client:
                try:
                    services = await client.get_services()
                except Exception as e:
                    output.exception(str(e))
                    continue

            for service in services:
                if (service.uuid == self.serviceId):
                    output.debug(device.address + " found service: " + service.uuid)
                    for characteristic in service.characteristics:
                        if characteristic.uuid == self.characteristicId:
                            output.debug(device.address + " found characteristic: " + characteristic.uuid)
                            output.info("Found lighthouse '"+ device.name +"' identified by '"+ device.address +"'.")
                            # TODO: warn about low signal strength close to -110

                            if self.lighthouseType == 1:
                                lighthouses.append(LighthouseV1(device.address))
                            else:
                                lighthouses.append(LighthouseV2(device.address))

                            isLighthouse = True
            if not isLighthouse:
                output.info("Unable to communicate with lighthouse '" + device.name + "' identified by '" + device.address + "'.")

        return lighthouses
