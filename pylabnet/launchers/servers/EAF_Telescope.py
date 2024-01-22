import pyvisa

from pylabnet.hardware.ASCOM.EAF_Telescope import Driver
from pylabnet.network.core.generic_server import GenericServer
from pylabnet.network.client_server.EAF_Telescope import Service, Client
from pylabnet.utils.helper_methods import get_ip, hide_console, load_device_config


def launch(**kwargs):
    """ Connects to PM320E and instantiates server

    :param kwargs: (dict) containing relevant kwargs
        :logger: instance of LogClient for logging purposes
        :port: (int) port number for the Cnt Monitor server
    """

    try:
        settings = load_device_config('EAF_Telescope',
                                      kwargs['config'],
                                      logger=kwargs['logger']
                                      )
    except KeyError:
        kwargs['logger'].warn('No config file was provided')

    try:
        kwargs['logger'].info('Try to connect')
        #self, lib_path = "", device_id = 0, logger =None)
        pm = Driver(settings['lib_path'], kwargs['device_id'], logger=kwargs['logger'])
        kwargs['logger'].info('Successfully connected')
    # Handle error of wrong GPIB address by allowing user to select
    # NOTE: this will fail if used from the main script launcher, since script client
    # will automatically try to connect (even though server isn't launched)
    #
    # TLDR: if you want to use launch-control, please fill in GPIB variable with
    # the correct resource string
    except:
        kwargs['logger'].error('An error occured while creating Object of EAF_Telescope')

    pm_service = Service()
    pm_service.assign_module(module=pm)
    pm_service.assign_logger(logger=kwargs['logger'])
    pm_server = GenericServer(
        service=pm_service,
        host=get_ip(),
        port=kwargs['port']
    )
    pm_server.start()
