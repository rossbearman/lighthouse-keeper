#!/usr/bin/env python3

import argparse
import asyncio
import os
import sys
from lighthouse import Lighthouse, LighthouseV1, LighthouseV2
from locator import LighthouseLocator
from output import output
from bleak import discover, BleakClient

parser = argparse.ArgumentParser(description='Discover and control SteamVR lighthouses')
parser.add_argument('lighthouseType', choices=[1, 2], type=int,
                    help='The version of the lighthouses you wish to communicate with')
parser.add_argument('command', choices=['discover', 'on', 'off'],
                    help='The command to execute')
parser.add_argument('lighthouseIdentifiers', nargs='*', default=[],
                    help='One or more lighthouse MAC addresses')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Print out additional information for debugging purposes')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.0',
                    help='Display the version number')

args = parser.parse_args()

output.initialise(args.debug)

async def run(loop):
    if args.command == "on" or args.command == "off":
        if not args.lighthouseIdentifiers:
            parser.print_usage()
            sys.exit(sys.argv[0] + ': error: you must specify at least one MAC address when calling `on` or `off`')

        lighthouses = []

        for lighthouseId in args.lighthouseIdentifiers:
            if args.lighthouseType == 1:
                lighthouses.append(LighthouseV1(lighthouseId))
            else:
                lighthouses.append(LighthouseV2(lighthouseId))

        for lighthouse in lighthouses:
            await lighthouse.runCommand(loop, args.command)

    if args.command == "discover":
        locator = LighthouseLocator(args.lighthouseType)

        output.info("Searching for lighthouses, this may take several minutes.\n")

        lighthouses = await locator.discover()

        if not lighthouses:
            output.info("No lighthouses found.")
        else:
            output.info("Finished.\n")
            print("If you are using MixedVR Manager, copy the following line to your config.bat:\n")
            print("set lighthouseMACAddressList=" + " ".join(lighthouse.mac for lighthouse in lighthouses))

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
