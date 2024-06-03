#important imports
from pyvisa import ResourceManager
from pylabnet.utils.logging.logger import LogHandler
import serial #for connection to arduino via usb
import cv2


class Driver:
    def __init__(self, minVoltage, maxVoltage, distanceToPicture, port='COM3', baudrate=115200, bitsResolution=10, logger=None):  # noqa: E501

        #initiate log: For logging in pylabnet
        self.log = LogHandler(logger=logger)
        self.rm = ResourceManager()
        self.log.info("Arduino-Logger established :)")

        #arduino code
        self.port = port
        self.baudrate = baudrate

        #Connect to Arduino
        try:
            self.arduino = serial.Serial(self.port, baudrate=115200, timeout=.1)
            self.log.info(f"Successfully connected to Arduino.")
        except:
            self.log.info("Error while Connecting. Wrong Port? Used port: " + self.port)

        #This is atm not impoortant and does not work
        self.minVoltage = minVoltage
        self.maxVoltage = minVoltage
        self.MirrorMaxVoltage = -5
        self.MirrorMaxVoltage = 5
        self.distance = distanceToPicture

        #actual important variables
        self.bitResolution = bitsResolution

        #maybe safe this in file an load.
        self.xCenter = 0
        self.yCenter = 0

        if self.MirrorMaxVoltage < self.minVoltage:
            self.log.info("Careful. Maximum applyable voltage is " + self.maxVoltage + " Volts. Spectra of Mirror is -5 to 5 Volts for 60°")

        self.maxUsageAngle = 60 * self.maxVoltage / self.MirrorMaxVoltage
        self.minimumAngle = self.maxUsageAngle / 2**(self.bitResolution)

        #might be a code idea in future. Maybe just set them to xCenter and yCenter
        #self.setDefaultCoords(500,500)
        #self.send_area_scan_0to1024(200,200, times = 10)

    #This functions sets the Galvo on the centercoords

    def setDefaultCoords(self, x_default, y_default):
        self.xCenter = x_default
        self.yCenter = y_default
        self.arduino.write(bytes("center" + ";" + str(x_default) + ";" + str(y_default), 'utf-8'))
        #adjust in future such that Arduino sends back a message if it is done

    #Sets the voltage of the DAC0 or DAC1 to a specific value. Therfore set x and cords to specific value
    def applyVoltageToDAC0to1024(self, DAC_pin, steps):

        amountOfSteps = steps # noqa: E501
        try:
            self.arduino.write(bytes(DAC_pin + ";" + str(amountOfSteps), 'utf-8'))
            data = self.arduino.readline()
            return data

        except:
            self.log.critical("Error occured while trying to write to the Arduino. Is he connected, is the rigth port used?")
            return "Error"

        return data

    #This sends a command to arduino to scan specific area. It is possible to set the center of the scan
    #x_steps and y_steps are the amount of steps the galvo should take in x and y direction. Its basiccally the size of the area scanned
    def send_area_scan_0to1024(self, x_steps, y_steps, x_center=-1, y_center=-1, times=10):
        self.log.info("Sending times" + str(times))
        if x_center != -1 or y_center != -1:
            messageToSend = "areaStep" + ";" + str(x_center) + ";" + str(y_center) + ";" + str(x_steps) + ";" + str(y_steps) + ";" + str(times)
            self.arduino.write(bytes("areaStep" + ";" + str(x_center) + ";" + str(y_center) + ";" + str(x_steps) + ";" + str(y_steps) + ";" + str(times), 'utf-8'))
            self.log.info("Sending: " + messageToSend)

        else:
            messageToSend = "areaStep" + ";" + str(self.xCenter) + ";" + str(self.yCenter) + ";" + str(x_steps) + ";" + str(y_steps) + ";" + str(times)
            self.arduino.write(bytes("areaStep" + ";" + str(self.xCenter) + ";" + str(self.yCenter) + ";" + str(x_steps) + ";" + str(y_steps) + ";" + str(times), 'utf-8'))
            #print("Sending: "+messageToSend)
            self.log.info("Sending: " + messageToSend)

        self.log.info("Please wait until arduino is finished")

        message = ""
        # while message == "" or message == b'':
        #     message = self.arduino.readline(4)

        return message

    #this is just a fun function with which one can draw a picture with the laser

    def makeLaserPicture(self, path=""):

        #fn = path
        im_gray = cv2.imread('herzz.png', cv2.IMREAD_GRAYSCALE)
        im_gray = cv2.resize(im_gray, (100, 100), interpolation=cv2.INTER_LINEAR)  # noqa: E501

        img_blur = cv2.GaussianBlur(im_gray, (3, 3), 0)
        sobelxy = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5)
        cv2.imshow('Sobel X Y using Sobel() function', sobelxy)
        #cv2.waitKey(0)
        edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200) # Canny Edge Detection
        # # Display Canny Edge Detection Image
        cv2.imshow('Canny Edge Detection', edges)
        #cv2.waitKey(0)

        im_gray = edges // 255
        img_list = im_gray.tolist()
        result = ""
        for row in img_list:
            row_str = [str(p) for p in row]
            result += "".join(row_str)

        result = "" + result
        # #send to arduino:
        print(result, file=open('Output.txt', 'w'))

        self.arduino.write(bytes("pict" + ";", 'utf-8'))
        print("go")

        #wait for answer
        message = ""
        while message == "" or message == b'':
            message = self.arduino.readline(4)

        return message
        #time.sleep(5)
        #print(self.arduino.readline())

        #print(result)

    #This function should allow the user to set one specific center for the laser to hit
    #def moveCenter(self):
        # with pynput.keyboard.Listener(on_release=on_key_release) as listener:
        #     listener.join()

        # if pynput.keyboard.Key() == key.right:
        #     self.arduino.write("DAC1")


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

#a= Driver(1, 1024,1,port = 'COM3', baudrate = 115200, bitsResolution = 10)
#a.setDefaultCoords(512,512)
# a.send_area_scan_0to1024(500,500,times =10)
# print(a.applyVoltageToDAC0to1024("DAC0",1023))
# print(a.applyVoltageToDAC0to1024("DAC1",1023))
#pm =Driver(0, 1024,1,port = 'COM3', baudrate = 115200, bitsResolution = 10,logger = logger)
#pm = Driver(0.535, 2.75, 1.0, port = 'COM3', baudrate = 115200, bitsResolution = 10, logger=None)
