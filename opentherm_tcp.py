from opentherm import OTGWClient
import logging

log = logging.getLogger(__name__)

class OTGWTcpClient(OTGWClient):
    r"""
    A skeleton for a TCP-client based
    """

    def open(self):
        r"""
        Open the connection to the OTGW

        Must be overridden in implementing classes. Called before reading of
        the data starts. Should not return until the connection is opened, so
        an immediately following call to `read` does not fail.
        """
        # TODO: Implement
        raise NotImplementedError("Not implemented yet")

    def close(self):
        r"""
        Close the connection to the OTGW

        Must be overridden in implementing classes. Called after reading of
        the data is finished. Should not return until the connection is closed.
        """
        # TODO: Implement
        raise NotImplementedError("Not implemented yet")

    def write(self, data):
        r"""
        Write data to the OTGW

        Must be overridden in implementing classes. Called when a command is
        received that should be sent to the OTGW. Should pass on the data
        as-is, not appending line feeds, carriage returns or anything.
        """
        # TODO: Implement
        raise NotImplementedError("Not implemented yet")

    def read(self, timeout):
        r"""
        Read data from the OTGW

        Must be overridden in implementing classes. Called in a loop while the
        client is running. May return any block of data read from the
        connection, be it line by line or any other block size. Must return a
        string. Line feeds and carriage returns should be passed on unchanged.
        Should adhere to the timeout passed. If only part of a data block is
        read before the timeout passes, return only the part that was read
        successfully, even if it is an empty string.
        """
        # TODO: Implement
        raise NotImplementedError("Not implemented yet")
