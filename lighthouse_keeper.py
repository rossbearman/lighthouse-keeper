#!/usr/bin/env python3

import argparse
import asyncio
import os
import sys
from lighthouse import Lighthouse, LighthouseV1, LighthouseV2
from locator import LighthouseLocator
from output import output
from bleak import discover, BleakClient

async def run(loop):
    if ARGS.command == "on" or ARGS.command == "off":
        if not ARGS.lighthouse_identifiers:
            PARSER.print_usage()
            sys.exit(sys.argv[0] + ': error: you must specify at least one MAC address when calling `on` or `off`')

        lighthouses = []

        for lighthouse_id in ARGS.lighthouse_identifiers:
            if ARGS.lighthouse_type == 1:
                lighthouses.append(LighthouseV1(lighthouse_id))
            else:
                lighthouses.append(LighthouseV2(lighthouse_id))

        for lighthouse in lighthouses:
            await lighthouse.run_command(loop, ARGS.command)

    if ARGS.command == "discover":
        locator = LighthouseLocator(ARGS.lighthouse_type)

        output.info("Searching for lighthouses, this may take several minutes.\n")

        lighthouses = await locator.discover()

        if not lighthouses:
            output.info("No lighthouses found.")
        else:
            output.info("Finished.\n")
            print("If you are using MixedVR Manager, copy the following line to your config.bat:\n")
            print("set lighthouseMACAddressList=" + " ".join(lighthouse.mac for lighthouse in lighthouses))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Discover and control SteamVR lighthouses')
    parser.add_argument('lighthouse_type', choices=[1, 2], type=int,
                        help='The version of the lighthouses you wish to communicate with')
    parser.add_argument('command', choices=['discover', 'on', 'off'],
                        help='The command to execute')
    parser.add_argument('lighthouse_identifiers', nargs='*', default=[],
                        help='One or more lighthouse MAC addresses')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Print out additional information for debugging purposes')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1.1',
                        help='Display the version number')

    return parser

if __name__ == "__main__":
    PARSER = parse_arguments()
    ARGS = PARSER.parse_args()

    output.initialise(ARGS.debug)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
