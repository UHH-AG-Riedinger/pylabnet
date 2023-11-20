from pyvisa import VisaIOError, ResourceManager
import numpy as np

from pylabnet.utils.logging.logger import LogHandler


class Driver:

    def __init__(self, usb_address=None, logger=None):
        """Instantiate driver class.

        :usb_address: USB-address of the scope, e.g. 'USB0::0x1313::0x8076::M00999999::INSTR'
            or simply to part address '0x1313::0x8076::M00999999'
            Can be read out by using
                rm = pyvisa.ResourceManager()
                rm.list_resources()
        :logger: An instance of a LogClient.
        """

        # Instantiate log.
        self.log = LogHandler(logger=logger)

        self.rm = ResourceManager()

        try:
            if usb_address.startswith('USB'):
                #full address, try to connect
                self.device = self.rm.open_resource(usb_address)
            else:
                #device ID, independent of adress
                res_list = self.rm.list_resources()
                visa_address = None
                for instr in res_list:
                    if instr.find(usb_address) >= 0:
                        visa_address = instr
                        break
                if visa_address is None:
                    self.log.info(f"No resource found {usb_address}.")
                    raise VisaIOError()
                self.device = self.rm.open_resource(visa_address)
            device_id = self.device.query('*IDN?')
            self.log.info(f"Successfully connected to {device_id}.")
            # We set a more forgiving timeout of 10s (default: 2s).
            # self.device.timeout = 10000
        except VisaIOError:
            self.log.error(f"Connection to {usb_address} failed.")

    def get_power(self):
        """ Returns the current power in watts on a desired channel

        :return: (float) power in watts
        """

        power = self.device.query(f'MEAS:POW?')
        return float(power)

    def get_wavelength(self):
        """ Returns the current wavelength in nm for the desired channel

        :return: (int) wavelength
        """

        wavelength = self.device.query(f'SENS:CORR:WAV?')
        return int(float(wavelength))

    def set_wavelength(self, wavelength):
        """ Sets the wavelength

        :param wavelength: (int) channel to set wavelength of
        """

        self.device.write(f'SENS:CORR:WAV {wavelength}')

    def get_range(self):
        """ Returns the current power range

        :return: (str) range
        """

        pr = self.device.query(f'SENS:POW:RANG?')
        return pr

    def set_range(self, p_range):
        """ Sets the range

        :param channel: (int) channel to set range of
        :param p_range: (str) range string identifier, can be anything in
            'AUTO', 'R1NW', 'R10NW', 'R100NW', 'R1UW', 'R10UW', 'R100UW', 'R1MW',
            'R10MW', 'R100MW', 'R1W', 'R10W', 'R100W', 'R1KW'
        """

        self.device.write(f'SENS:POW:RANG {p_range}')

    def get_range_auto(self):
        """ Returns the current power range for the channel

        :return: (str) range
        """

        pr = self.device.query(f'SENS:POW:RANG:AUTO?')
        return pr

    def set_range_auto(self, p_range):
        """ Sets the range

        :param channel: (int) channel to set range of
        :param p_range: (str) range string identifier, can be anything in
            'OFF', '0' 'ON*' '1'
        """

        self.device.write(f'SENS:POW:RANG:AUTO {p_range}')


def get_driver_args(device_config, logger=None):
    #device_type = 'thorlabs_pm101' #could be extracted from file name
    #try:
    #    device_config = load_device_config(device_type, config, logger=logger)
    #except KeyError:
    #    logger.warn('No config file was provided')
    driver_args = {
        "usb_address": device_config['device_id'],
        "logger": logger
    }
    return driver_args
