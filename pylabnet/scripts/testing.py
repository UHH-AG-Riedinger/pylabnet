from pyvisa import ResourceManager
from pylabnet.utils.logging.logger import LogHandler
import serial #for connection to arduino via usb
import cv2
import time

arduino = serial.Serial('COM8', 9600, timeout=.1)
time.sleep(2)
arduino.write(b'ON\n')

"""

import serial
import time

# Replace 'COM8' with your port name
arduino_port = 'COM8'
baud_rate = 9600  # Must match the rate used in the Arduino sketch

# Establish a connection to the Arduino
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Wait for the connection to initialize

def turn_on():
    ser.write(b'ON\n')  # Send "ON" command

def turn_off():
    ser.write(b'OFF\n')  # Send "OFF" command

# Turn the laser on and off
turn_on()

"""
