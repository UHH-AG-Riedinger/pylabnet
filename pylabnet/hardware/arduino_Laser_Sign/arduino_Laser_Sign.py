#important imports
from pyvisa import ResourceManager
from pylabnet.utils.logging.logger import LogHandler
import serial #for connection to arduino via usb
import cv2
import time


class Driver:
    def __init__(self, port='COM8', baudrate=9600, logger=None):  # noqa: E501

        #initiate log: For logging in pylabnet
        self.log = LogHandler(logger=logger)
        self.rm = ResourceManager()
        self.log.info("Arduino-Logger established :)")

        #arduino code
        self.port = port
        self.baudrate = baudrate

        #Connect to Arduino
        try:
            self.arduino = serial.Serial(self.port, baudrate=9600, timeout=.1)
            time.sleep(1)
            self.log.info(f"Successfully connected to Arduino_Laser_Sign.")
        except:
            self.log.info("Error while Connecting. Wrong Port? Used port: " + self.port)

        #self.turn_on()
        #self.log.info("Arduino_Laser_Sign is on.")

    def turn_on(self):
        self.arduino.write(b'ON\n')  # Send "ON" command

    def turn_off(self):
        self.arduino.write(b'OFF\n')  # Send "OFF" command

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
