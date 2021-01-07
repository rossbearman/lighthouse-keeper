# Lighthouse Keeper
Discover and control SteamVR lighthouses (versions 1.0 and 2.0)

## Prerequisites
### Binary
* Windows 10
* Bluetooth 4.0/BLE chip (integrated or external), managed by Windows

### Python Script
* Python 3
* bleak BLE library, minimum version 0.10.0

## Usage and Examples

Search the local environment for lighthouses: `./lighthouse-keeper.exe discover`

Once you have the MAC addresses of the lighthouses you wish to control, you must specify the command you wish to send (`on`/`off`), the version of the lighthouses (`1`/`2`) and then a space-separated list of MAC addresses for the devices to send the command to.

Typically, HTC Vive lighthouses with the flat front are version 1.0 (`1`) and Valve-branded lighthouses with the curved front are 2.0 (`2`). The output of `discover` will tell you which versions it has found.

Turn the specified 1.0 lighthouses on: `./lighthouse-keeper.exe on 1 80:7A:BF:15:1F:88 80:7A:BF:15:28:8C`

Turn the specified 2.0 lighthouses off: `./lighthouse-keeper.exe off 2 FE:D0:49:F5:78:D6 E2:81:7F:AC:2B:ED`

## Troubleshooting
### Debug / Verbose Mode
Add the `-d` flag to any command to print additional information (including BLE signal strength) and a log file which includes further information from the Bluetooth library.

### Cannot find or control lighthouses
This commonly occurs if Windows does not have control of the Bluetooth stack, usually because a manufacturer driver is being used instead, such as CSR Harmony. Uninstalling these and rebooting or re-inserting the Bluetooth dongle should resolve this issue.

### HTC 1.0 lighthouses do not respond
When you first run `discover`, Windows should prompt you to pair each device, you will need to do this within a few seconds or the notification will disappear and the script will terminate. Once you've done this once, the script should work correctly.

## Compiling an Executable
PyInstaller is used to generate an executable from the source. Run the following command in the root folder:

`pyinstaller --onefile .\lighthouse_keeper.py`

If you install PyInstaller via `pip`, Windows Defender will often flag any compiled executables. You can typically fix this by compiling PyInstaller's bootloader yourself and installing it manually, rather than using `pip`.

1. `git clone https://github.com/pyinstaller/pyinstaller`
2. `cd pyinstaller/bootloader`
3. `py ./waf distclean all`
4. `cd ..`
5. `py setup.py install`

## Acknowledgements
[monstermac77](https://github.com/monstermac77) and [PumkinSpice](https://github.com/PumkinSpice) for their work on the [MixedVR Manager](https://github.com/monstermac77/vr), the [WMR MixedVR guide](https://github.com/PumkinSpice/MixedVR/wiki/ReadMe) and their extensive testing of this script.

The following two projects figured out the required GATT characteristics and values to discover and control the headsets. This project was initially a from-scratch rewrite of these designed to make integration with MixedVR Manager easier.

* [nouser2013](https://github.com/nouser2013) for [lighthouse-v2-manager](https://github.com/nouser2013/lighthouse-v2-manager)
* [ihainan](https://github.com/ihainan) for [lighthouse-v1-manager](https://github.com/ihainan/lighthouse-v1-manager)

Finally, [Ben Woodford](https://gist.github.com/BenWoodford/) for their exploration and [documentation](https://gist.github.com/BenWoodford/3a1e500a4ea2673525f5adb4120fd47c) of the 2.0 GATT characteristics and [nairol](https://github.com/nairol) for their [1.0 basestation documentatrion](https://github.com/nairol/LighthouseRedox/blob/master/docs/Base%20Station.md).
