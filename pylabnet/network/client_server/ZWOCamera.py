from pylabnet.network.core.service_base import ServiceBase
from pylabnet.network.core.client_base import ClientBase


class Service(ServiceBase):
    def exposed_take_picture(self, name=""):
        return self._module.take_picture(name)


class Client(ClientBase):
    def take_picture(self, name=""):
        return self._service.exposed_take_picture(name)
