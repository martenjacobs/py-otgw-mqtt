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
        print (self._args['ipadress'],self._args['port'])
        self._socket.connect((self._args['ipadress'], self._args['port']))

    def close(self):
        r"""
        Close the connection to the OTGW
        """
        self._socket.close()

    def write(self, data):
        r"""
        Write data to the OTGW
        """
        self._socket.sendall("{}\r\n".format(data.rstrip('\r\n')))
   

    def read(self):
        r"""
        Read data from the OTGW
        """
   
        return self._socket.recv(128).decode()
      
