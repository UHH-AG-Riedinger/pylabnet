from pylabnet.network.client_server.m2_solstis import Service, Client
from pylabnet.hardware.lasers.m2_solstis import Driver
from pylabnet.utils.helper_methods import GenericServer, get_ip, load_device_config


def launch(**kwargs):

    config_dict = load_device_config('m2_solstis', kwargs['config'], kwargs['logger'])
    tisa = Driver(ip=config_dict['ip'],
                  port1=config_dict['port1'],
                  port2=config_dict['port2'],
                  logger=kwargs['logger'])

    tisa_service = Service()
    tisa_service.assign_module(module=tisa)
    tisa_service.assign_logger(logger=kwargs['logger'])
    tisa_server = GenericServer(
        service=tisa_service,
        host=get_ip(),
        port=kwargs['port']
    )
    tisa_server.start()
