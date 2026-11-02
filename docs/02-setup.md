# 2. Hardware and software you need

## Hardware

| What | Why |
|---|---|
| **K+DCAN USB cable** (OBD2, FTDI chip, with the pin 7/8 switch) | Connects the laptop to the car. Cheap clones work, FTDI-based ones are the most reliable |
| **Windows laptop** | The MS45 Flasher and TunerPro only run on Windows |
| **Battery charger or power supply, 13.5-14 V** | Voltage must not drop during flashing. Do not rely on the battery alone |

## Software

| What | Where | For |
|---|---|---|
| MS45 Flasher | [terraphantm/MS45-Flasher](https://github.com/terraphantm/MS45-Flasher), Releases | Reading and flashing |
| TunerPro RT | [tunerpro.net](https://www.tunerpro.net) | Editing the file with the XDF |
| Python 3 | [python.org](https://www.python.org) | Running `ms45_check.py` (Windows, macOS or Linux) |
| INPA or another BMW diagnostic tool | | Reading and clearing fault memory |
| This repository | "Code" button, "Download ZIP" | XDF and check script |

## Setting up the cable

1. Install the FTDI driver for the cable.
2. Device Manager, Ports, your USB serial port, Properties, Port Settings, Advanced: set **Latency Timer to 1 ms**. Note the COM port number.
3. With a switchable cable (pin 7/8 switch): set it as the cable seller describes for your car's build date. If the flasher cannot identify the DME, try the other position.

## Before every session

- Charger connected and switched on.
- Laptop on mains power, sleep and standby turned off.
- Lights, radio, fan and other consumers off.
- Ignition on, engine off.
