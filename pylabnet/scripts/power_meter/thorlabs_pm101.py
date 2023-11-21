import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
import pyvisa
import time
import numpy as np

logger = lg.LogClient()

pmX = hm.autoconnect_device(device_tag='red power meter', logger=logger)

for i in range(5):
    power = pmX.get_power()
    print(power)
    time.sleep(1)
