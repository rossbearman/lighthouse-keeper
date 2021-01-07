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

        devices = await discover()

        potential_lighthouses = filter(None, map(self._create_lighthouse_from_device, devices))

        lighthouses = []

        for lighthouse in potential_lighthouses:
            if await self._is_device_lighthouse(lighthouse):
                lighthouses.append(lighthouse)

        return lighthouses

    def _create_lighthouse_from_device(self, device):
        """Create the appropriate Lighthouse object for a given BLEDevice

        Args:
            device (BLEDevice): A BLEDevice that may or may not be a lighthouse
        Returns:
            Union(LighthouseV1, LighthouseV2, None)
        """

        if device.name.startswith(LighthouseV1.name_prefix):
            output.debug(device.address + ": potential 1.0 lighthouse '" + device.name +"'")
            output.debug(device.address + ": signal strength is " + str(device.rssi))

            return LighthouseV1(device.address, device.name)
        elif device.name.startswith(LighthouseV2.name_prefix):
            output.debug(device.address + ": potential 2.0 lighthouse '" + device.name +"'")
            output.debug(device.address + ": signal strength is " + str(device.rssi))

            return LighthouseV2(device.address, device.name)
        else:
            return None

    async def _is_device_lighthouse(self, lighthouse):
        """Determine if a device is a lighthouse we can communicate with.

        Args:
            lighthouse (Union[LighthouseV1, LighthouseV2]): An instance of LighthouseV1 or LighthouseV2
        Returns:
            bool
        """

        async with BleakClient(lighthouse.address) as client:
            try:
                services = await client.get_services()
            except Exception as e:
                output.exception(str(e))
                return False

        for service in services:
            if self._service_has_lighthouse_characteristics(service, lighthouse):
                return True

        return False

    def _service_has_lighthouse_characteristics(self, service, lighthouse):
        """Determine if the passed service has the correct characteristics for power management.

        Args:
            service (BleakGATTServiceCollection): The GATT service collection from a potential lighthouse
            lighthouse (Union[LighthouseV1, LighthouseV2]): An instance of LighthouseV1 or LighthouseV2
        Returns:
            bool
        """
        if (service.uuid != lighthouse.service):
            return False

        output.debug(lighthouse.address + ": found service '" + service.uuid + "'")

        for characteristic in service.characteristics:
            if characteristic.uuid == lighthouse.characteristic:
                output.debug(lighthouse.address + ": found characteristic '" + characteristic.uuid + "'")
                output.debug(lighthouse.address + ": is a valid " + str(lighthouse.version) + ".0 lighthouse")
                return True

        return False

