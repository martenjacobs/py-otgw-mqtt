from opentherm import OTGWClient, ConnectionException
import logging
import socket
import select

log = logging.getLogger(__name__)

class OTGWTcpClient(OTGWClient):
    r"""
    A skeleton for a TCP-client based
    """

    def __init__(self, listener, **kwargs):
        super(OTGWTcpClient, self).__init__(listener)
        self._host = kwargs['host']
        self._port = int(kwargs['port'])
        self._socket = None

    def open(self):
        r"""
        Open the connection to the OTGW
        """
        try:
          self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          self._socket.connect((self._host, self._port))
          self._socket.setblocking(0)
        except socket.error as e:
            log.warn("Failed to close socket: {}".format(e))
            raise ConnectionException(str(e))

    def close(self):
        r"""
        Close the connection to the OTGW
        """
        try:
            self._socket.close()
        except socket.error as e:
            log.warn("Failed to close socket: {}".format(e))

    def write(self, data):
        r"""
        Write data to the OTGW

        Packet inspection with wireshark of the original otmonitor learned
        that the command must only be terminated with a \r and not with \r\n
        """
        try: 
            self._socket.sendall("{}\r".format(data.rstrip('\r\n')).encode())
        except socket.error as e:
            log.warn("Failed to write: {}".format(e))
            raise ConnectionException(str(e))

    def read(self, timeout):
        r"""
        Read data from the OTGW
        """
        # This blocks until the socket is ready or the timeout has passed
        try:
            ready = select.select([self._socket], [], [], timeout)
            if ready[0]:
                return self._socket.recv(128).decode()              
        except socket.error as e:
            log.warn("Failed to read: {}".format(e))
            raise ConnectionException(str(e))
        return ""
