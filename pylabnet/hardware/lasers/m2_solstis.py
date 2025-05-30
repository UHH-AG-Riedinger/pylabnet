
# -*- coding: utf-8 -*-
"""
This module controls an M squared laser
Originally taken from:
https://github.com/AlexShkarin/pyLabLib/blob/master/pylablib/aux_libs/devices/M2.py
Modifications by Graham Joe, M. Chalupnik
"""

import socket
import json
import websocket
from pylabnet.utils.logging.logger import LogHandler

BUFFERSIZE = 2048
MIN_WAVELENGTH = 650
MAX_WAVELENGTH = 1100


class Driver():

    def __init__(self, ip, port1, port2, timeout=50, logger=None):

        self.buffersize = BUFFERSIZE
        self._timeout = timeout
        self.address1 = (ip, port1)
        self.address2 = (ip, port2)
        self.client_address = ('192.168.1.102', 17495)#57605)
        self.transmission_id = 1
        self.log = LogHandler(logger)
        self._last_status = {}
        # self.log.info('Connecting to M2 Solstis at {}'.format(self.address1))
        print('Connecting to M2 Solstis at {}'.format(self.address1))
        self.connect_laser()

    def connect_laser(self):
        """ Connect to Instrument.
        @return bool: connection success
        """
        self.socket = socket.create_connection(self.address1, timeout=self._timeout)
        # self.update_socket = socket.create_connection(self.address2, timeout=self._timeout)
        print("socket and update socket created")
        self.log.info("socket and update socket created")
        interface = self.socket.getsockname()[0]
        _, reply = self.send('start_link', {'ip_address': interface})
        # _, reply2 = self.send('start_link', {'ip_address': interface}, socket=2)
        if reply['status'] == 'ok': #and reply2['status'] == 'ok':
            print("Laser connection established")
        else:
            raise Exception('Laser connection failed')

    def disconnect_laser(self):
        """ Close the connection to the instrument.
        """
        self.socket.close()
        self.update_socket.close()

    def ping_laser(self):
        """ Checks if the laser is connected.
        """
        _, reply = self.send('ping', {'text_in': 'check'})
        print(reply)
        # _, reply2 = self.send('ping', {'text_in': 'check'}, socket=2)
        return True

    def send(self, op, parameters, transmission_id=None, report=False, socket=1):
        """ Send json message to laser
        :param op: operation to be performed
        :param parameters: dictionary of parameters associated with op
        :param transmission_id: optional transmission id integer
        :param report: request completion report (doesn't apply to all operations)
        :return: reply operation dictionary, reply parameters dictionary
        """
        if report:
            parameters["report"] = "finished"
            self._last_status[op] = {}
        message = self._build_message(op, parameters, transmission_id)
        self.log.info("message:")
        self.log.info(message)
        print(message)
        if socket == 1:
            self.flush()
            self.socket.sendall(message.encode('utf-8'))
            reply = self.socket.recv(self.buffersize)
            self.log.info("reply:")
            self.log.info(reply)
            print(reply)
        # elif socket == 2:
        #     self.update_socket.sendall(message.encode('utf-8'))
        #     reply = self.update_socket.recv(self.buffersize)
        #     self.log.info(reply)
        op_replies, parameters_replies = self._parse_reply(reply)
        # for op_reply, parameters_reply in zip(op_replies, parameters_replies):
        # self._last_status[self._parse_report_op(op_reply)] = parameters_reply
        return op_replies[-1], parameters_replies[-1]

    def flush(self, bits=100000, timeout=0):
        """ Flush read buffer, may cause socket timeout if used when laser isn't scanning
        """
        timeout = max(timeout, 0.001)
        self.socket.settimeout(timeout)
        try:
            return self.socket.recv(bits)
        except:
            pass
        self.socket.settimeout(self._timeout)

    tuning_commands = {"tune_etalon": "tune_etalon",
                       "tune_reference_cavity": "tune_cavity",
                       "fine_tune_reference_cavity": "fine_tune_cavity",
                       "tune_resonator": "tune_resonator",
                       "fine_tune_resonator": "fine_tune_resonator"}
    tuning_states = ["tuning operation completed", "tuning setting out of range", "tuning command failed"]

    def tune(self, tune_type, percent, report=False):
        """Tune the etalon to percent. Only works if the wavemeter is disconnected.
        :param tune_type: see tuning commands above
        :param percent: percent to tune etalon to
        :param report: request completion report
        """
        _, parameters_reply = self.send(self.tuning_commands[tune_type], {"setting": [percent]}, report=report)
        reply_status = parameters_reply["status"][0]
        if reply_status != 0:
            self.log.warn(self.tuning_states[reply_status])

    def get_voltage(self, transmission_id=None):
        """ Get the current voltage of the laser.
        :param transmission_id: optional transmission id integer
        :return: reply operation dictionary, reply parameters dictionary
        """
        op = 'get_status'
        params = {}
        if transmission_id is None:
            transmission_id = self.transmission_id
        _, reply = self.send(op, params, transmission_id)
        return reply['resonator_voltage'][0]

    def set_voltage(self, voltage, max_voltage, report=False):
        """copy of the tune function for wlm_monitor_RR.
        Uses fine tune resonator command. Voltage has to be converted to percent.
        Tune the resonator to percent. Only works if the wavemeter is disconnected.
        :param tune_type: see tuning commands above
        :param voltage: voltage
        :param max_voltage: maximum voltage
        :param report: request completion report
        """

        percent = voltage / max_voltage * 100
        tune_type = "tune_resonator"
        _, parameters_reply = self.send(self.tuning_commands[tune_type], {"setting": [percent]}, report=report)
        reply_status = parameters_reply["status"][0]
        if reply_status != 0:
            self.log.warn(self.tuning_states[reply_status])

    def get_status(self, transmission_id=None):
        """ Get the status of the laser
        :param transmission_id: optional transmission id integer
        :return: reply operation dictionary, reply parameters dictionary
        """
        op = 'get_status'
        params = {}
        if transmission_id is None:
            transmission_id = self.transmission_id
        _, reply = self.send(op, params, transmission_id)
        return reply

    def _build_message(self, op, params, transmission_id=None):
        """ Builds a json message in standard format to be sent to the laser
        :param op: operation to be performed by the laser
        :param params: parameters dictionary associated with the operation
        :param transmission_id: optional transmission id integer
        :return: json byte string to be send to the laser
        """
        if transmission_id is None:
            self.transmission_id = self.transmission_id % 16383 + 1
        else:
            self.transmission_id = transmission_id
        message = {'message': {'transmission_id': [self.transmission_id], 'op': op, 'parameters': dict(params)}}
        return json.dumps(message)

    _parse_errors = ["unknown", "JSON parsing error", "'message' string missing",
                     "'transmission_id' string missing", "No 'transmission_id' value",
                     "'op' string missing", "No operation name",
                     "operation not recognized", "'parameters' string missing", "invalid parameter tag or value"]

    def _parse_reply(self, reply):
        """ Parses a json reply from the laser into lists of the two relevant dictionaries
        :param reply: json reply from laser
        :return: list of reply operation dictionaries, list of reply parameters dictionaries
        """
        # Initialize operation and reply dictionary lists
        op_reply = []
        parameters_reply = []

        # Decode the ICE-BLOC reply with the appropriate delimeters between individual messages
        reply = reply.decode("utf-8")
        preplies = self._parse_messages('[' + reply.replace('}{', '},{') + ']')

        # Log any parsing errors and append messages parsed into dictionaries to output lists
        for preply in preplies:
            if preply["op"] == "parse_fail":
                parameters = preply["parameters"]
                error = parameters["protocol_error"][0]
                error_description = "unknown" if error >= len(self._parse_errors) else self._parse_errors[error]
                error_message = "device parse error: transmission_id={}, error={}({}), error point='{}'".format(
                    parameters.get("transmission", ["NA"])[0], error, error_description,
                    parameters.get("JSON_parse_error", "NA"))
                self.log.warn(error_message)
            op_reply.append(preply["op"])
            parameters_reply.append(preply["parameters"])
        return op_reply, parameters_reply

    def _parse_messages(self, message):
        """ Parses a standard format json message into a dictionary
        :param message: json string
        :return: message dictionary
        """
        # Disregard partial messages cut off by the buffer size
        if len(message) >= self.buffersize:
            self.log.warn('Message size >= buffer size, increase buffer read rate and/or buffer size to avoid '
                          'missing information')
            # split from right
            msg = message.rsplit('},{', 1)
            message = msg[0]
            # split from left
            msg = message.split('},{', 1)
            message = msg[1]
            message = '[{' + message + '}]'

        # Parse message according to the json protocol, extract the useful part and log ICE-BLOC protocol violations
        parsed_messages = json.loads(message)
        for n, parsed_message in enumerate(parsed_messages):
            if 'message' not in parsed_message:
                self.log.warn("coudn't decode message: {}".format(message))
            parsed_message = parsed_message['message']
            parsed_messages[n] = parsed_message
            for key in ['transmission_id', 'op', 'parameters']:
                if key not in parsed_message:
                    self.log.warn("parameter '{}' not in the message {}".format(key, message))
        return parsed_messages

    # def _parse_report_op(self, op):
        """Remove the final report suffix from an operation
        :param op: original operation
        :return string: parsed operation
        """
        if op == self._terascan_update_op:
            return op
        elif op[-4:] == '_f_r':
            return op[:-4]
        else:
            return op[:-6]
