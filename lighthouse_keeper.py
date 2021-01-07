#!/usr/bin/env python3

import argparse
import asyncio
import sys
from lighthouse import Lighthouse, LighthouseV1, LighthouseV2
from locator import LighthouseLocator
from output import output

async def run(loop):
    if ARGS.command == "on" or ARGS.command == "off":
        if not ARGS.lighthouse_addresses:
            PARSER.print_usage()
            sys.exit(sys.argv[0] + ': error: you must specify at least one MAC address when calling `on` or `off`')

        for address in ARGS.lighthouse_addresses:
            if ARGS.lighthouse_version == 1:
                lighthouse = LighthouseV1(address)
            else:
                lighthouse = LighthouseV2(address)

            await lighthouse.run_command(loop, ARGS.command)

    if ARGS.command == "discover":
        output.info("Searching for lighthouses, this may take several minutes.\n")

        locator = LighthouseLocator()
        lighthouses = await locator.discover()

        if not lighthouses:
            output.info("No lighthouses found.")
        else:
            output.info("Finished.\n")
            print("If you are using MixedVR Manager, copy the following line to your config.bat:\n")
            print("set lighthouseMACAddressList=" + " ".join(lighthouse.address for lighthouse in lighthouses))

def parse_arguments():
    parser = argparse.ArgumentParser(description='Discover and control SteamVR lighthouses')
    parser.add_argument('command', choices=['discover', 'on', 'off'],
                        help='The command to execute')
    parser.add_argument('lighthouse_version', choices=[1, 2], type=int, nargs='?', default=0,
                        help='The version of the lighthouses you wish to communicate with')
    parser.add_argument('lighthouse_addresses', nargs='*', default=[],
                        help='One or more lighthouse MAC addresses')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Print out additional information for debugging purposes')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.3.0',
                        help='Display the version number')

    return parser

if __name__ == "__main__":
    PARSER = parse_arguments()
    ARGS = PARSER.parse_args()

    output.initialise(ARGS.debug)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
