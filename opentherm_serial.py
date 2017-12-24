from opentherm import OTGWClient
import re
from threading import Lock, Thread
import logging
import serial

log = logging.getLogger(__name__)

class OTGWSerialClient(OTGWClient):
    r"""
    A serial-based OTGWClient implementation
    """

    def __init__(self, listener, **kwargs):
        super(OTGWSerialClient, self).__init__(listener)
        self._args=kwargs

    def open(self):
        r"""
        Open the serial connection
        """
        # TODO: Move other settings to config
        self._serial = serial.Serial(self._args['device'],
            baudrate=self._args.get('baudrate', 9600),
            bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE, timeout=0.1)

    def close(self):
        r"""
        Close the serial connection
        """
        self._serial.close()

    def write(self, data):
        r"""
        Write data to the serial device
        """
        self._serial.write("{}\r\n".format(data.rstrip('\r\n')))
        self._serial.flush()

    def read(self, timeout):
        r"""
        Read a block of data from the serial device
        """
        if(self._serial.timeout != timeout):
            self._serial.timeout = timeout
        return self._serial.read(128)
