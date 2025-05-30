from pylabnet.network.client_server.m2_solstis import Service, Client
from pylabnet.hardware.lasers.m2_solstis import Driver
from pylabnet.network.core.generic_server import GenericServer
from pylabnet.utils.helper_methods import get_ip, load_device_config


def launch(**kwargs):

    tisa_logger = kwargs['logger']
    config_dict = load_device_config('m2_solstis', kwargs['config'], kwargs['logger'])

    tisa = Driver(ip=config_dict['ip'],
                  port1=config_dict['port1'],
                  port2=config_dict['port2'],
                  logger=tisa_logger)
    tisa_logger.info('TISA server started.')
    # Instantiate server
    tisa_service = Service()
    tisa_service.assign_module(module=tisa)
    tisa_service.assign_logger(logger=tisa_logger)
    tisa_server = GenericServer(
        service=tisa_service,
        host=get_ip(),
        port=kwargs['port'],
    )
    tisa_server.start()
