import re
from threading import Lock, Thread
from time import sleep
import logging
import collections

log = logging.getLogger(__name__)

# Default namespace for the topics. Will be overwritten with the value in
# config
topic_namespace="value/otgw"

# Parse hex string to int
def hex_int(hex):
    return int(hex, 16)

# Pre-compile a regex to parse valid OTGW-messages
line_parser = re.compile(
    r'^(?P<source>[BART])(?P<type>[0-9A-F])(?P<res>[0-9A-F])'
    r'(?P<id>[0-9A-F]{2})(?P<data>[0-9A-F]{4})$'
)


def flags_msg_generator(ot_id, val):
    r"""
    Generate the pub-messages from a boolean value.

    Currently, only flame status is supported. Any other items will be returned
    as-is.

    Returns a generator for the messages
    """
    yield ("{}/{}".format(topic_namespace, ot_id), val, )
    if(ot_id == "flame_status"):
        yield ("{}/flame_status_ch".format(topic_namespace),
               val & ( 1 << 1 ) > 0, )
        yield ("{}/flame_status_dhw".format(topic_namespace),
               val & ( 1 << 2 ) > 0, )
        yield ("{}/flame_status_bit".format(topic_namespace),
               val & ( 1 << 3 ) > 0, )

def float_msg_generator(ot_id, val):
    r"""
    Generate the pub-messages from a float-based value

    Returns a generator for the messages
    """
    yield ("{}/{}".format(topic_namespace, ot_id), round(val/float(256), 2), )

def int_msg_generator(ot_id, val):
    r"""
    Generate the pub-messages from an integer-based value

    Returns a generator for the messages
    """
    yield ("{}/{}".format(topic_namespace, ot_id), val, )

def get_messages(message):
    r"""
    Generate the pub-messages from the supplied OT-message

    Returns a generator for the messages
    """
    info = line_parser.match(message)
    if info is None:
        if message:
            log.debug("Did not understand message: '{}'".format(message))
        return iter([])
    (source, ttype, res, did, data) = \
        map(lambda f, d: f(d),
            (str, lambda _: hex_int(_) & 7, hex_int, hex_int, hex_int),
            info.groups())
    if source not in ('B', 'T', 'A') \
        or ttype not in (1,4) \
        or did not in opentherm_ids:
        return iter([])
    id_name, parser = opentherm_ids[did]
    return parser(id_name, data)


# Map the opentherm ids (named group 'id' in the line parser regex) to
# discriptive names and message creators. I put this here because the
# referenced generators have to be assigned first
opentherm_ids = {
	0:   ("flame_status",flags_msg_generator,),
	1:   ("control_setpoint",float_msg_generator,),
	9:   ("remote_override_setpoint",float_msg_generator,),
	14:  ("max_relative_modulation_level",float_msg_generator,),
	16:  ("room_setpoint",float_msg_generator,),
	17:  ("relative_modulation_level",float_msg_generator,),
	18:  ("ch_water_pressure",float_msg_generator,),
	24:  ("room_temperature",float_msg_generator,),
	25:  ("boiler_water_temperature",float_msg_generator,),
	26:  ("dhw_temperature",float_msg_generator,),
	27:  ("outside_temperature",float_msg_generator,),
	28:  ("return_water_temperature",float_msg_generator,),
	56:  ("dhw_setpoint",float_msg_generator,),
	57:  ("max_ch_water_setpoint",float_msg_generator,),
	116: ("burner_starts",int_msg_generator,),
	117: ("ch_pump_starts",int_msg_generator,),
	118: ("dhw_pump_starts",int_msg_generator,),
	119: ("dhw_burner_starts",int_msg_generator,),
	120: ("burner_operation_hours",int_msg_generator,),
	121: ("ch_pump_operation_hours",int_msg_generator,),
	122: ("dhw_pump_valve_operation_hours",int_msg_generator,),
	123: ("dhw_burner_operation_hours",int_msg_generator,)
}

class OTGWClient(object):
    r"""
    An abstract OTGW client.

    This class can be used to create implementations of OTGW clients for
    different types of communication protocols and technologies. To create a
    full implementation, only four methods need to be implemented.
    """
    def __init__(self, listener, **kwargs):
        self._worker_running = False
        self._listener = listener
        self._worker_thread = None
        self._send_buffer = collections.deque()

    def open(self):
        r"""
        Open the connection to the OTGW

        Must be overridden in implementing classes. Called before reading of
        the data starts. Should not return until the connection is opened, so
        an immediately following call to `read` does not fail.
        """
        raise NotImplementedError("Abstract method")

    def close(self):
        r"""
        Close the connection to the OTGW

        Must be overridden in implementing classes. Called after reading of
        the data is finished. Should not return until the connection is closed.
        """
        raise NotImplementedError("Abstract method")

    def write(self, data):
        r"""
        Write data to the OTGW

        Must be overridden in implementing classes. Called when a command is
        received that should be sent to the OTGW. Should pass on the data
        as-is, not appending line feeds, carriage returns or anything.
        """
        raise NotImplementedError("Abstract method")

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
        raise NotImplementedError("Abstract method")

    def join(self):
        r"""
        Block until the worker thread finishes
        """
        self._worker_thread.join()

    def start(self):
        r"""
        Connect to the OTGW and start reading data
        """
        if self._worker_thread:
            raise RuntimeError("Already running")
        self._worker_thread = Thread(target=self._worker)
        self._worker_thread.start()

    def stop(self):
        r"""
        Stop reading data and disconnect from the OTGW
        """
        if not self._worker_thread:
            raise RuntimeError("Not running")
        self._worker_running = False
        self.join()

    def reconnect(self):
        r"""
        Attempt to reconnect when the connection is lost
        """
        try:
            self.close()
        except Exception:
            pass

        while self._worker_running:
            try:
                self.open()
                break
            except Exception as e:
                log.warn(("Could not reconnect: {}. "
                         "Will retry in 10 seconds").format(e.message))
                sleep(10)

    def send(self, data):
        self._send_buffer.append(data)

    def _worker(self):
        # _worker_running should be True while the worker is running
        self._worker_running = True

        # Open the connection to the OTGW
        self.open()

        # Compile a regex that will only match the first part of a string, up
        # to and including the first time a line break and/or carriage return
        # occurs. Match any number of line breaks and/or carriage returns that
        # immediately follow as well (effectively discarding empty lines)
        line_splitter = re.compile(r'^.*[\r\n]+')

        # Create a buffer for read data
        data = ""

        while self._worker_running:
            # Call the read method of the implementation
            try:
                while self._send_buffer:
                    self.write(self._send_buffer[0])
                    self._send_buffer.popleft()

                data += self.read(timeout=0.5) or ""
            except ConnectionException:
                log.warn("Connection lost, will attempt to reconnect")
                self.reconnect()
            # Find all the lines in the read data
            while True:
                m = line_splitter.match(data)
                if not m:
                    # There are no full lines yet, so we have to read some more
                    break

                # Get all the messages for the line that has been read,
                # most lines will yield no messages or just one, but
                # flags-based lines may return more than one.
                for msg in get_messages(m.group().rstrip('\r\n')):
                    try:
                        # Pass each message on to the listener
                        self._listener(msg)
                    except Exception as e:
                        # Log a warning when an exception occurs in the
                        # listener
                        log.warn(str(e))

                # Strip the consumed line from the buffer
                data = data[m.end():]

        # After the read loop, close the connection and clean up
        self.close()
        self._worker_thread = None

class ConnectionException(Exception):
    def __init__(self, message):
        super(ConnectionException, self).__init__(message)
