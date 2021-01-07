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
    lighthouse_type : int
        The version of SteamVR lighthouse to search for, 1 or 2
    """

    def __init__(self, lighthouse_type):
        self.lighthouse_type = lighthouse_type

        if lighthouse_type == 1:
            self.name_prefix = LighthouseV1.name_prefix
            self.service_id = LighthouseV1.service
            self.characteristic_id = LighthouseV1.characteristic
        else:
            self.name_prefix = LighthouseV2.name_prefix
            self.service_id = LighthouseV2.service
            self.characteristic_id = LighthouseV2.characteristic

    async def discover(self):
        lighthouses = []
        devices = await discover()
        for device in devices:
            is_lighthouse = False

            if device.name.find(self.name_prefix) != 0:
                continue

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
                if (service.uuid == self.service_id):
                    output.debug(device.address + " found service: " + service.uuid)
                    for characteristic in service.characteristics:
                        if characteristic.uuid == self.characteristic_id:
                            output.debug(device.address + " found characteristic: " + characteristic.uuid)
                            output.info("Found lighthouse '"+ device.name +"' identified by '"+ device.address +"'.")
                            # TODO: warn about low signal strength close to -110

                            if self.lighthouse_type == 1:
                                lighthouses.append(LighthouseV1(device.address))
                            else:
                                lighthouses.append(LighthouseV2(device.address))

                            is_lighthouse = True
            if not is_lighthouse:
                output.info("Unable to communicate with lighthouse '" + device.name + "' identified by '" + device.address + "'.")

        return lighthouses
