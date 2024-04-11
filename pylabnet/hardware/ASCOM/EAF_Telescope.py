import ctypes
from pyvisa import ResourceManager
from pylabnet.utils.logging.logger import LogHandler


class Driver:
    def __init__(self, lib_path="", device_id=0, logger=None):

        #prepare logging asnd connect logger
        self.log = LogHandler(logger=logger)
        self.rm = ResourceManager()
        self.log.info("EAF-Logger established :)")

        #prepare libary of EAF
        self.lib_path = lib_path
        self.device_id = device_id
        #self.lib = ctypes.cdll.LoadLibrary(lib_path)

        try:
            self.lib = ctypes.cdll.LoadLibrary(lib_path)
            self.log.info("Libary geladen")
        except:
            self.log.info("Error while loading Libary. Wrong Path? Used path: " + lib_path)

        #load ID-List of ASCOM devices. Without this the EAF ID won't be found
        self.log.info("Number of Ascom devices: " + str(self.EAFGetNum()))
        #open the device
        #print(self.EAFGetNum())
        self.EAFopen()
        # try:
        #     self.EAFmove(1000)
        #     time.sleep(1)
        #     self.log.info(self.EAFis_moving())
        #     self.EAFstop()
        #     self.log.info(self.EAFis_moving())

        # except:
        #     self.log.info("Error while  moving")

    def EAFGetNum(self):
        """ Descriptions:
        This should be the first API to be called
        get number of connected EAF focuser, call this API to refresh device list if EAF is connected
        or disconnected

        Return: number of connected EAF focuser. 1 means 1 focuser is connected.
        """

        num_devices = self.lib.EAFGetNum()
        return num_devices

    def EAFopen(self):
        self.log.info("Try to open EAF")
        back = self.lib.EAFOpen(int(self.device_id))

        if back != 0:
            self.log.info("An error occured while opening the EAF device. Error code: " + str(back))

    def EAFclose(self):
        return self.lib.EAFClose(self.device_id)

    def EAFCheck(self, pid):
        #VID is 0x03C3 for EAF
        # Check if an EAF device with the specified Vendor ID (vid) and Product ID (pid) is connected
        is_connected = self.lib.EAFCheck(0x03C3, ctypes.c_uint16(pid))
        return is_connected

    def EAFGetID(self, index):
        # Get the ID of the EAF device at the specified index
        PointerInt = ctypes.c_int()
        id = self.lib.EAFGetID(int(index), ctypes.byref(PointerInt))
        return PointerInt.value, id

    def EAFget_position(self):
        position = ctypes.c_int()
        self.lib.EAFGetPosition(int(self.device_id), ctypes.byref(position))
        return position.value

    def EAFGetSDKVersion(self):
        # Get the SDK version of the EAF library
        sdk_version = self.lib.EAFGetSDKVersion()
        return sdk_version

    def EAFmove(self, steps):
        return self.lib.EAFMove(int(self.device_id), int(steps))

    def EAFstop(self):
        self.lib.EAFStop(int(self.device_id))

    def EAFis_moving(self):
        is_moving = ctypes.c_bool()
        is_hand_control = ctypes.c_bool()
        self.lib.EAFIsMoving(int(self.device_id), ctypes.byref(is_moving), ctypes.byref(is_hand_control))
        return is_moving.value

    def EAFResetPosition(self, steps):
        # Reset the position of the EAF device with the specified ID to the specified number of steps
        return self.lib.EAFResetPostion(int(self.device_id), int(steps))

    def EAFgetTemp(self):
        temperature = ctypes.c_float()
        self.lib.EAFGetTemp(self.device_id, ctypes.byref(temperature))
        return temperature.value

    def EAFset_beep(self, beep):
        # Enable or disable the beep sound for the EAF device with the specified ID
        self.lib.EAFSetBeep(self.device_id, beep)

    def EAFget_beep(self):
        # Check if the beep sound is enabled for the EAF device with the specified ID
        is_beep = ctypes.c_bool()
        self.lib.EAFGetBeep(self.device_id, ctypes.byref(is_beep))
        return is_beep.value

    def EAFget_backlash(self):
        # Get the backlash of the EAF device with the specified ID
        backlash = ctypes.c_int()
        self.lib.EAFGetBacklash(self.device_id, ctypes.byref(backlash))
        return backlash.value

    def EAFset_backlash(self, backlash_value):
        #Set the backlash of the EAF device with the specified ID
        self.lib.EAFSetBacklash(self.device_id, backlash_value)

    def EAFget_reverse(self):
        # Get the reverse status of the EAF device with the specified ID
        is_reverse = ctypes.c_bool()
        self.lib.EAFGetReverse(self.device_id, ctypes.byref(is_reverse))
        return is_reverse.value

    def EAFset_reverse(self, reverse_status):
        # Set the reverse status of the EAF device with the specified ID
        self.lib.EAFSetReverse(self.device_id, reverse_status)

    def EAFstep_range(self):
        # Get the step range of the EAF device with the specified ID
        step_range = ctypes.c_int()
        self.lib.EAFStepRange(self.device_id, ctypes.byref(step_range))
        return step_range.value

    def EAFget_max_step(self):
        # Get the max range of the EAF device with the specified ID

        max_range = ctypes.c_int()
        error_code = self.lib.EAFGetMaxStep(self.device_id, ctypes.byref(max_range))
        return max_range.value

    def EAFSetMaxStep(self, max_step):
        # Set the maximum step value of the EAF device with the specified ID
        error_code = self.lib.EAFSetMaxStep(self.device_id, max_step)
