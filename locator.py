#!/usr/bin/env python3

import asyncio
from lighthouse import LighthouseV1, LighthouseV2
from bleak import discover, BleakClient
from output import output

class LighthouseLocator():
    """Discover lighthouses in the local environment via Bluetooth
    """

    async def discover(self):
        lighthouses = []
        devices = await discover()
        for device in devices:
            if device.name.find(LighthouseV1.name_prefix) == 0:
                potential_lighthouse = LighthouseV1(device.address)
            elif device.name.find(LighthouseV2.name_prefix) == 0:
                potential_lighthouse = LighthouseV2(device.address)
            else:
                continue

            output.debug(device.address + ": potential " + str(potential_lighthouse.version) + ".0 lighthouse '" + device.name +"'")
            output.debug(device.address + ": signal strength is " + str(device.rssi))

            is_lighthouse = await self.is_device_lighthouse(device, potential_lighthouse)

            if not is_lighthouse:
                output.info("Unable to communicate with lighthouse '" + device.name + "' identified by '" + device.address + "'.")
                continue

            lighthouses.append(potential_lighthouse)

            output.info("Found " + str(potential_lighthouse.version) + ".0 lighthouse '"+ device.name +"' identified by '"+ device.address +"'.")

        return lighthouses

    async def is_device_lighthouse(self, device, potential_lighthouse):
        async with BleakClient(device.address) as client:
            try:
                services = await client.get_services()
            except Exception as e:
                output.exception(str(e))
                return False

        for service in services:
            if self.service_has_lighthouse_characteristics(service, potential_lighthouse):
                return True

        return False

    def service_has_lighthouse_characteristics(self, service, potential_lighthouse):
        if (service.uuid != potential_lighthouse.service):
            return False

        output.debug(potential_lighthouse.address + ": found service '" + service.uuid + "'")

        for characteristic in service.characteristics:
            if characteristic.uuid == potential_lighthouse.characteristic:
                output.debug(potential_lighthouse.address + ": found characteristic '" + characteristic.uuid + "'")
                return True

        return False

