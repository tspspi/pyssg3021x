from labdevices.functiongenerator import FunctionGenerator, FunctionGeneratorWaveform, FunctionGeneratorModulation
from labdevices.exceptions import CommunicationError_ProtocolViolation, CommunicationError_Timeout, CommunicationError_NotConnected
from labdevices.scpi import SCPIDeviceEthernet

from time import sleep

import atexit
import struct

import socket

class SSG3021X(FunctionGenerator):
    def __init__(
            self,
            address = None,
            port = 5025,

            logger = None
    ):
        self._scpi = SCPIDeviceEthernet(address, port, logger)

        self._usedConnect = False
        self._usedContext = False
        super().__init__(
            nchannels = 1,
            freqrange = (9e3, 2.1e9),
            amplituderange = (-90, 20),
            offsetrange = (0,0),

            arbitraryWaveforms = False,
            arbitraryWaveformLength = (0,0),
            arbitraryWaveformMinMax = (0,0),
            hasFrequencyCounter = False,

            supportedWaveforms = [
                FunctionGeneratorWaveform.SINE
            ]
        )

        atexit.register(self.__close)

    def _connect(self, address = None, port = None):
        if self._scpi.connect():
            # Ask for identity and verify
            v = self._id()
            self._serialno = v['serial']
            self._versions = v['version']

        return True

    def _disconnect(self):
        self._scpi.disconnect()

    def _isConnected(self):
        return self._scpi.isConnected()

    def __enter__(self):
        if self._usedConnect:
            raise ValueError("Cannot use context management on connected port")
        self._connect()
        self._usesContext = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__close()
        self._usesContext = False

    def __close(self):
        atexit.unregister(self.__close)
        if self._socket is not None:
            # TODO: Disable output port
            self._disconnect()

    def _id(self):
        res = self._scpi.scpiQuery("*IDN?")
        res = res.split(",")
        if len(res) != 4:
            raise CommunicationError_ProtocolViolation("IDN string does not follow siglents layout")
        if res[0] != "Siglent Technologies":
            raise CommunicationError_ProtocolViolation(f"IDN returned manufacturer {res[0]}")
        if res[1] != "SSG3021X":
            raise CommunicationError_ProtocolViolation(f"IDN does not identify SSG3021X")

        ver = res[3].split(".")
        ver[2] = ver[2].split("R")

        return {
            'type' : res[1],
            'serial' : res[2],
            'version' : [
                ver[0],
                ver[1],
                ver[2][0],
                ver[2][1]
            ]
        }
    def _serial(self):
        return self._id['serial']

    def _set_channel_waveform(self, channel = None, waveform = None, arbitrary = None):
        # Parent class filters to allow only SINE
        return True
    def _get_channel_waveform(self, channel = None):
        return FunctionGeneratorWaveform.SINE
    def _set_channel_frequency(self, channel = None, frequency = None):
        self._scpi.scpiCommand(f"FREQ {frequency}")
        return True
    def _get_channel_frequency(self, channel = None):
        dta = self._scpi.scpiQuery("FREQ?")
        return float(dta)
    def _set_channel_amplitude(self, channel = None, amplitude = None):
        self._scpi.scpiCommand(f"POW {amplitude}")
        return True
    def _get_channel_amplitude(self, channel = None):
        dta = self._scpi.scpiQuery("POW?")
        return float(dta)
    def _set_channel_enabled(self, channel = None, enable = None):
        if enable:
            self._scpi.scpiCommand(":OUTP ON")
        else:
            self._scpi.scpiCommand(":OUTP OFF")
        return True
    def _is_channel_enabled(self, channel = None):
        res = self._scpi.scpiQuery(":OUTP?")
        if int(res) == 1:
            return True
        else:
            return False
