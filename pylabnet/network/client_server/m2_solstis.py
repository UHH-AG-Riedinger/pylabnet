

from pylabnet.network.core.service_base import ServiceBase
from pylabnet.network.core.client_base import ClientBase


class Service(ServiceBase):
    def exposed_connect_laser(self):
        return self._module.connect_laser()


class Client(ClientBase):

    def connect_laser(self):
        return self._service.exposed_connect_laser()
