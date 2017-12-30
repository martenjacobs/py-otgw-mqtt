from opentherm import OTGWClient
import logging
import socket

log = logging.getLogger(__name__)

class OTGWTcpClient(OTGWClient):
    r"""
    A skeleton for a TCP-client based
    """

    def __init__(self, listener, **kwargs):
        super(OTGWTcpClient, self).__init__(listener)
        self._args=kwargs

    def open(self):
        r"""
        Open the connection to the OTGW
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._args['ipadress'], self._args['port']))

    def close(self):
        r"""
        Close the connection to the OTGW
        """
        self._socket.close()

    def write(self, data):
        r"""
        Write data to the OTGW

        Packet inspection with wireshark of the original otmonitor learned
        that the command must only be terminated with a \r and not with \r\n
        """
        self._socket.sendall("{}\r".format(data.rstrip('\r\n')).encode())
   

    def read(self):
        r"""
        Read data from the OTGW
        """
        return self._socket.recv(128).decode()
      
