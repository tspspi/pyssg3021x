# (Unofficial) SSG3021X function generator control library

![SSG3021X function generator](https://github.com/tspspi/pyssg3021x/blob/master/doc/devicephoto.png)

This is a simple (currently incomplete) implementation of
the [FunctionGenerator baseclass](https://github.com/tspspi/pylabdevs/blob/master/src/labdevices/functiongenerator.py)
of the [pylabdevs base classes](https://github.com/tspspi/pylabdevs) for the
Siglent SSG3021X function generator. It establishes a connection via
Ethernet and allows currently to:

* Set and query frequency of the RF port
* Enable and disable the RF port
* Setting the power on the RF port

## Installation

This package is available as PyPi package ```ssg3021x-tspspi```:

```
pip install ssg3021x-tspspi
```

## Usage

### Simple example (with context management)

```
from ssg3021x.ssg3021x import SSG3021X
from time import sleep

with SSG3021X("198.51.100.1") as ssg:
	# Ask for identification
	print(ssg.identify())

	# Set frequency to 200 MHz, 10 dBm output power and enable output
	ssg.set_channel_frequency(0, 202e6)
	ssg.set_channel_amplitude(0, 10)
	ssg.set_channel_enabled(0, True)

	# Query status
	print(f"Frequency:\t{ssg.get_channel_frequency()}")
	print(f"Amplitude:\t{ssg.get_channel_amplitude()}")
	print(f"Enabled:\t{ssg.is_channel_enabled()}")

	# Wait
	sleep(60)

	# Disable
	ssg.set_channel_enabled(0, False)
```
