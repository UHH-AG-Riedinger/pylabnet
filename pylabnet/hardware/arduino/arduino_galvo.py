import numpy as np
from pyvisa import VisaIOError, ResourceManager
from pylabnet.utils.logging.logger import LogHandler
import serial
import cv2


print('hallo ich bin der driver')

class Driver:
    def __init__(self, minVoltage, maxVoltage, distanceToPicture, port = 'COM3', baudrate = 115200, bitsResolution = 10, logger=None):  # noqa: E501
        
        #initiate log:
        
        self.log = LogHandler(logger=logger)
        self.rm = ResourceManager()
        self.log.info("1YAY :)")

        #arduino code
        self.port = port
        self.baudrate = baudrate

        #Connect to Arduino
        try:
            self.log.info("YAY :)")
            self.arduino = serial.Serial(self.port,  baudrate=115200, timeout=.1)
            self.log.info(f"Successfully connected to Arduino.")
        except:
            print("Error while Connecting. Wrong Port? Used port: "+self.port)



        self.minVoltage = minVoltage
        self.maxVoltage = minVoltage
        self.MirrorMaxVoltage = -5
        self.MirrorMaxVoltage = 5
        self.bitResolution = bitsResolution
        self.distance = distanceToPicture
        self.xCenter = 0
        self.yCenter = 0
        
        #maybe safe this in file an load.
        self.xCenter = 0
        self.yCenter = 0

        if self.MirrorMaxVoltage < self.minVoltage:
            print("Careful. Maximum applyable voltage is "+self.maxVoltage+" Volts. Spectra of Mirror is -5 to 5 Volts for 60°")

        self.maxUsageAngle = 60*self.maxVoltage/self.MirrorMaxVoltage
        self.minimumAngle = self.maxUsageAngle / 2**(self.bitResolution)

        #setDefaultCoords(500,400)
        #time.sleep(0.2)
        #send_area_scan_0to1024(700,700,times=100) #good is 350, 300 for scanning area
        
        #time.sleep(0.8)



    def setDefaultCoords(self, x_default, y_default):
        self.xCenter = x_default
        self.yCenter = y_default
        self.arduino.write(bytes("center"+";"+str(x_default)+";"+str(y_default),  'utf-8'))

    #Length Informations making no sense right now. Maybe later
    # def applyVoltageToDAC(self, DAC_pin, movingLength):
    
    #     amountOfSteps = int(round(np.arcsin(movingLength/self.distance)/(self.minimumAngle/360*2*np.pi)))  # noqa: E501
    #     self.arduino.write(bytes(DAC_pin+";"+str(amountOfSteps),  'utf-8'))

    #     data = self.arduino.readline()

    
    def applyVoltageToDAC0to1024(self, DAC_pin, steps ):
    
        amountOfSteps = steps # noqa: E501
        try:
            self.arduino.write(bytes(DAC_pin+";"+str(amountOfSteps),  'utf-8'))
            data = self.arduino.readline()
            return data
        
        except:
            print("Error occured while trying to write to the Arduino. Is he connected, is the rigth port used?")
            return "Error"
        
    #Length Information are useless right now. Maybe later
    # def send_area_scan_Length(self, x_length, y_hight):
    #     messageToSend = "area"+";"+str(x_length)+";"+str(y_hight)+";"+str(self.distance)
    #     self.arduino.write(bytes("area"+";"+str(x_length)+";"+str(y_hight)+";"+str(self.distance),  'utf-8'))
    #     print("Sending: "+messageToSend)
    #     time.sleep(0.1)
    #     data = self.arduino.readline()#

        return data
    
    def send_area_scan_0to1024(self, x_steps, y_steps, x_center = -1, y_center=-1, times = 100):

        if x_center != -1 or y_center != -1:
            messageToSend = "areaStep"+";"+str(x_center)+";"+str(y_center)+";"+str(x_steps)+";"+str(y_steps)+";"+str(times)
            self.arduino.write(bytes("areaStep"+";"+str(x_center)+";"+str(y_center)+";"+str(x_steps)+";"+str(y_steps)+";"+str(times),  'utf-8'))
            print("Sending: "+messageToSend)
        
        else:
            messageToSend = "areaStep"+";"+str(self.xCenter)+";"+str(self.yCenter)+";"+str(x_steps)+";"+str(y_steps)+";"+str(times)
            self.arduino.write(bytes("areaStep"+";"+str(self.xCenter)+";"+str(self.yCenter)+";"+str(x_steps)+";"+str(y_steps)+";"+str(times),  'utf-8'))
            print("Sending: "+messageToSend)


        
        print("Please wait until arduino is finished")

        message = ""
        while message == "" or message == b'':
            message = self.arduino.readline(4)
        
        return message


    def makeLaserPicture(self, path = ""):

        #fn = path
        im_gray = cv2.imread('herzz.png', cv2.IMREAD_GRAYSCALE)
        im_gray = cv2.resize(im_gray,(100,100),interpolation= cv2.INTER_LINEAR)  # noqa: E501

        img_blur = cv2.GaussianBlur(im_gray, (3,3), 0)
        sobelxy = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=5)
        cv2.imshow('Sobel X Y using Sobel() function', sobelxy)
        #cv2.waitKey(0)
        edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200) # Canny Edge Detection
        # # Display Canny Edge Detection Image
        cv2.imshow('Canny Edge Detection', edges)
        #cv2.waitKey(0)

        im_gray = edges//255
        img_list = im_gray.tolist()
        result = ""
        for row in img_list:
            row_str = [str(p) for p in row]
            result +=  "".join(row_str)

        result = ""+ result
        # #send to arduino:
        print(result,  file=open('C:\\Users\\timoe\\OneDrive\\Desktop\\Output.txt', 'w'))
        
        self.arduino.write(bytes("pict"+";", 'utf-8'))
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
# a.send_area_scan_0to1024(500,500,times =100)
# print(a.applyVoltageToDAC0to1024("DAC0",1023))
# print(a.applyVoltageToDAC0to1024("DAC1",1023))
#pm =Driver(0, 1024,1,port = 'COM3', baudrate = 115200, bitsResolution = 10,logger = logger)
#pm = Driver(0.535, 2.75, 1.0, port = 'COM3', baudrate = 115200, bitsResolution = 10, logger=None)
