from pylabnet.network.core.service_base import ServiceBase
from pylabnet.network.core.client_base import ClientBase


class Service(ServiceBase):

    def exposed_setDefaultCoords(self, x_default, y_default):
        return self._module.setDefaultCoords(x_default, y_default)

    def exposed_applyVoltageToDAC0to1024(self, DAC_pin, steps):
        return self._module.applyVoltageToDAC0to1024(DAC_pin, steps)

    def exposed_send_area_scan_0to1024(self, x_steps, y_steps, x_center=-1, y_center=-1, times=10):
        return self._module.send_area_scan_0to1024(x_steps, y_steps, x_center, y_center, times)

    def exposed_makeLaserPicture(self, path=""):
        return self._module.makeLaserPicture(path="")


class Client(ClientBase):

    def setDefaultCoords(self, x_default, y_default):
        return self._service.exposed_setDefaultCoords(x_default, y_default)

    def applyVoltageToDAC0to1024(self, DAC_pin, steps):
        return self._service.exposed_applyVoltageToDAC0to1024(DAC_pin, steps)

    def send_area_scan_0to1024(self, x_steps, y_steps, x_center=-1, y_center=-1, times=10):
        return self._service.exposed_send_area_scan_0to1024(x_steps, y_steps, x_center, y_center, times)

    def makeLaserPicture(self, path=""):
        return self._service.exposed_makeLaserPicture(path="")
