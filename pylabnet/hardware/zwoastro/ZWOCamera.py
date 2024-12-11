from pyvisa import ResourceManager
from pylabnet.utils.logging.logger import LogHandler
from datetime import datetime
import os


import zwoasi as asi
#todDO add zwoasi to requiments if it works


class Driver:
    def __init__(self, lib_path="", device_id=0, logger=None):

        #prepare logging asnd connect logger
        self.log = LogHandler(logger=logger)
        self.rm = ResourceManager()
        self.log.info("ZWOASI-Logger established :)")

        #prepare libary of EAF
        self.lib_path = lib_path
        self.device_id = device_id
        #self.lib = ctypes.cdll.LoadLibrary(lib_path)
        self.log.info(asi.init(lib_path))
        self.asi = asi

        #load ID-List of ZWOASI devices. Without this the EAF ID won't be found
        self.log.info("Number of Cameras connected: " + str(self.asi.get_num_cameras()))

        #set camera number to 1, has to be adjuste din the future when we have more cameras!
        self.camera_list = self.asi.list_cameras()  # Models names of the connected cameras
        self.num_cameras = self.asi.get_num_cameras()
        if self.num_cameras == 1:
            self.camera_id = 0
            self.log.info('Found one camera: %s' % self.camera_list[0])
        self.camera = self.asi.Camera(self.camera_id)
        self.log.info('Camera loaded:')
        self.camera.set_control_value(self.asi.ASI_BANDWIDTHOVERLOAD, self.camera.get_controls()['BandWidth']['MinValue'])
        self.camera.disable_dark_subtract()

        self.camera.set_control_value(self.asi.ASI_GAIN, 25)
        self.camera.set_control_value(self.asi.ASI_EXPOSURE, 4000000)
        self.camera.set_control_value(asi.ASI_WB_B, 99)
        self.camera.set_control_value(asi.ASI_WB_R, 75)
        self.camera.set_control_value(asi.ASI_GAMMA, 50)
        self.camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
        self.camera.set_control_value(asi.ASI_FLIP, 0)

        today = datetime.now()
        directory = "C:/GithubSync/pictures taken/" + today.strftime('%Y%m%d')
        if os.path.isdir(directory) == False:
            os.mkdir(directory)
        self.camera.set_image_type(asi.ASI_IMG_RGB24)
        self.camera.capture(filename=directory + "/" + today.strftime('%H%M%S') + '.jpg')

        self.log.info('Saved to %s' % directory)

    def take_picture(self, name=""):
        today = datetime.now()
        if name != "":
            directory = "C:/GithubSync/pictures taken/" + name
        else:
            directory = "C:/GithubSync/pictures taken/" + today.strftime('%Y%m%d')
        if os.path.isdir(directory) == False:
            os.mkdir(directory)
        self.camera.set_image_type(asi.ASI_IMG_RGB24)
        self.camera.capture(filename=directory + "/" + today.strftime('%Y%m%d%H%M%S') + '.jpg')

        self.log.info('Saved to %s' % directory)
