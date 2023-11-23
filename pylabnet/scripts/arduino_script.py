import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
import pyvisa
import numpy as np


logger = lg.LogClient()

pmX = hm.autoconnect_device(device_tag='Arduino_Galvo', logger=logger)

print(pmX.send_area_scan_0to1024(500, 500, times=100))
