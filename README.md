# gigapy

This is a small program for controlling fan speeds on some Gigabyte motherboards, without using Gigabyte's GUI. It requires that Gigabyte's SIV (System Information Viewer) is installed.

## Rationale

On my machine, the Windows 10 Anniversary Update (version 1607) update broke the GUI portion of SIV (ThermalConsole.exe), but the daemon, thermald.exe, still worked.

My problems were on a machine with an AMD 990X chipset. I haven't tried reinstalling Windows 10 yet, and the different version of SIV for Intel did work on my friend's freshly installed Windows 10, with a Z170 chipset.

## How it works

### SIV

SIV's GUI can configure fixed or dynamic fan speeds, which are actuated by thermald.exe. thermald.exe reads its config from an XML file. I don't know exactly what ThermalConsole.exe does with thermald.exe, but it takes quite a while to make changes, so it may well just be restarting it.

### gigapy

gigapy calculates the desired fan speeds, writes them to thermald.exe's XML config, then restarts thermald.exe.

Currently, it requires that [OpenHardwareMonitor][1] is running, with CSV logging enabled.

## How to use
### Dependencies
* Python 3. Pip packages: `pip install -r requirements.txt`
* Gigabyte SIV
* [OpenHardwareMonitor][1]

### Configuration

* Set `OHMDir` in [server.py](server.py) (location of CSV files).
* Set `SIVDir` in [gigapy.py](gigapy.py) (location of thermald.exe, and a hidden Profile folder).

### Run

`python3 server.py`

## Notes

* There's hard-coded config which is specific to my PC, but it will be improved at some point.
* AMD only, but I think the only difference is that the Intel version reads from a single XMl file, in a different location.
* I kill the thermald.exe process shortly after I run it. This is because the way it naturally exits after several seconds kind of steals window focus.

## TODO

See the [issues][2] page.

## Contributions

They are welcome!

## License

[MIT](LICESNE.md)

[1]: https://github.com/openhardwaremonitor/openhardwaremonitor
[2]: https://github.com/DinCahill/gigapy/issues
