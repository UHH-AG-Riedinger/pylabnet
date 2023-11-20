import pyvisa
import importlib
import os

from pylabnet.hardware.power_meter.thorlabs_pm320e import Driver
from pylabnet.network.core.generic_server import GenericServer
from pylabnet.network.client_server.thorlabs_pm320e import Service, Client
from pylabnet.utils.helper_methods import get_ip, hide_console, load_device_config


def launch(**kwargs):
    """ Connects to PM320E and instantiates server

    :param kwargs: (dict) containing relevant kwargs
        :logger: instance of LogClient for logging purposes
        :port: (int) port number for the Cnt Monitor server
    """

    server = kwargs['device_type']

    try:
        device_config = load_device_config(server,
                                           kwargs['config'],
                                           logger=kwargs['logger']
                                           )
    except KeyError:
        kwargs['logger'].warn('No config file was provided')

    try:
        pylabnet_cs_inst = importlib.import_module(f'pylabnet.network.client_server.{server}')
    except ModuleNotFoundError:
        kwargs['logger'].error(f'No module found in pylabnet.network.client_server named {server}.py')
        raise

    try:
        instr_class = locate_server(server)
        if instr_class is not None:
            pylabnet_driver_inst = importlib.import_module(f'pylabnet.hardware.{instr_class}.{server}')
        else:
            kwargs['logger'].error(f'No module found in pylabnet.hardware named {server}.py')
            raise ModuleNotFoundError
    except ModuleNotFoundError:
        kwargs['logger'].error(f'No module found in pylabnet.hardware named {server}.py')
        raise

    try:
        #parameter_list = pylabnet_driver_inst.get_parameters()
        ##this should be a 2xN list, with keyword, and cofig_name. Will be unpacked to instantiate the driver
        #driver_args = dict()
        #for entry in parameter_list:
        #    driver_args[entry[0]] = device_config[entry[1]]
        #driver_args['logger'] = kwargs['logger']
        #alternatively, the driver could simply provide a function, constructs the input arguments
        driver_args = pylabnet_driver_inst.get_driver_args(device_config, logger=kwargs['logger'])
    except:
        kwargs['logger'].error(f'no parameter_list found in pylabnet.hardware.{server}')
        raise UnsupportedEasyLaunchException #not tested

    try:
        device = pylabnet_driver_inst.Driver(**driver_args)
    except:
        kwargs['logger'].error('easy launch failed.')
        raise UnsupportedEasyLaunchException

    device_service = pylabnet_cs_inst.Service()
    device_service.assign_module(module=device)
    device_service.assign_logger(logger=kwargs['logger'])
    device_server = GenericServer(
        service=device_service,
        host=get_ip(),
        port=kwargs['port']
    )
    device_server.start()


def locate_server(server):
    server_file = server + '.py'
    driver_base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'hardware'
                                   )
    with os.scandir(driver_base_dir) as it:
        for instr_class in it:
            if not instr_class.name.startswith('.') and instr_class.is_dir():
                with os.scandir(os.path.join(driver_base_dir, instr_class.name)) as drivers:
                    for driver in drivers:
                        if not driver.name.startswith('.') and driver.is_file() and (driver.name == server_file):
                            return instr_class.name
    return None


class UnsupportedEasyLaunchException(Exception):
    """Raised when the module does not support easy launch is not supported."""
