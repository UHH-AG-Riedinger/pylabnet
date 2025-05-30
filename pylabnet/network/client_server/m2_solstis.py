import pickle

from pylabnet.network.core.service_base import ServiceBase
from pylabnet.network.core.client_base import ClientBase


class Service(ServiceBase):
    def exposed_connect_laser(self):
        return self._module.connect_laser()

    def exposed_disconnect_laser(self):
        return self._module.disconnect_laser()

    def exposed_ping_laser(self):
        return self._module.ping_laser()

    def exposed_set_timeout(self, timeout):
        return self._module.set_timeout(timeout)

    def exposed_send(self, op, parameters, transmission_id=None, report=False, socket=1):
        return self._module.send(op, parameters, transmission_id, report, socket)

    # def exposed_set(self, setting, value, key_name='setting'):
    #     return self._module.set(setting, value, key_name)

    # def exposed_get(self, setting):
    #     return self._module.get(setting)

    def exposed_tune(self, tune_type, percent, report=False):
        return self._module.tune(tune_type, percent, report)

    def exposed_get_voltage(self):
        return self._module.get_voltage()

    def exposed_set_voltage(self, voltage, max_voltage, report=False):
        voltage = pickle.loads(voltage)
        max_voltage = pickle.loads(max_voltage)
        return self._module.set_voltage(voltage, max_voltage, report)

    def exposed_check_tuning_report(self, tune_type):
        return self._module.check_tuning_report(tune_type)

    def exposed_get_status(self, transmission_id=None):
        return self._module.get_status(transmission_id)


class Client(ClientBase):

    def connect_laser(self):
        return self._service.exposed_connect_laser()

    def disconnect_laser(self):
        return self._service.exposed_disconnect_laser()

    def ping_laser(self):
        return self._service.exposed_ping_laser()

    def set_timeout(self, timeout):
        return self._service.exposed_set_timeout(timeout)

    def send(self, op, parameters, transmission_id=None, report=False, socket=1):
        return self._service.exposed_send(op, parameters, transmission_id, report, socket)

    # def set(self, setting, value, key_name='setting'):
    #     return self._service.exposed_set(setting, value, key_name)

    # def get(self, setting):
    #     return self._service.exposed_get(setting)

    def tune(self, tune_type, percent, report=False):
        return self._service.exposed_tune(tune_type, percent, report)

    def get_voltage(self):
        return self._service.exposed_get_voltage()

    def set_voltage(self, voltage, max_voltage, report=False):
        voltage = pickle.dumps(voltage)
        max_voltage = pickle.dumps(max_voltage)
        return self._service.exposed_set_voltage(voltage, max_voltage, report)

    def check_tuning_report(self, tune_type):
        return self._service.exposed_check_tuning_report(tune_type)

    def get_status(self, transmission_id=None):
        return self._service.exposed_get_status(transmission_id)
