#!/usr/bin/env python3

import asyncio
from lighthouse import LighthouseV1, LighthouseV2
from bleak import discover, BleakClient
from output import output

class LighthouseLocator():
    """Discover lighthouses in the local environment via Bluetooth.
    """

    async def discover(self):
        """Discover all potential lighthouses in the local environment and check that we can control them.

        Returns:
            list: A collection of valid lighthouses.
        """

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

            is_lighthouse = await self._is_device_lighthouse(device, potential_lighthouse)

            if not is_lighthouse:
                output.info("Unable to communicate with lighthouse '" + device.name + "' identified by '" + device.address + "'.")
                continue

            lighthouses.append(potential_lighthouse)

            output.info("Found " + str(potential_lighthouse.version) + ".0 lighthouse '"+ device.name +"' identified by '"+ device.address +"'.")

        return lighthouses

    async def _is_device_lighthouse(self, device, potential_lighthouse):
        """Determine if a device is a lighthouse we can communicate with.

        Args:
            device (BLEDevice): The lighthouse's BLE device
            potential_lighthouse (Union[LighthouseV1, LighthouseV2]): An instance of LighthouseV1 or LighthouseV2
        Returns:
            bool
        """

        async with BleakClient(device.address) as client:
            try:
                services = await client.get_services()
            except Exception as e:
                output.exception(str(e))
                return False

        for service in services:
            if self._service_has_lighthouse_characteristics(service, potential_lighthouse):
                return True

        return False

    def _service_has_lighthouse_characteristics(self, service, potential_lighthouse):
        """Determine if the passed service has the correct characteristics for power management.

        Args:
            service (BleakGATTServiceCollection): The GATT service collection from a potential lighthouse
            potential_lighthouse (Union[LighthouseV1, LighthouseV2]): An instance of LighthouseV1 or LighthouseV2
        Returns:
            bool
        """
        if (service.uuid != potential_lighthouse.service):
            return False

        output.debug(potential_lighthouse.address + ": found service '" + service.uuid + "'")

        for characteristic in service.characteristics:
            if characteristic.uuid == potential_lighthouse.characteristic:
                output.debug(potential_lighthouse.address + ": found characteristic '" + characteristic.uuid + "'")
                return True

        return False

