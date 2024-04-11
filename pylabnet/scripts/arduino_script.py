import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
import pyvisa
import numpy as np


logger = lg.LogClient()

pmX = hm.autoconnect_device(device_tag='Arduino_Galvo', logger=logger)

a = 1
x = 512
y = 512
# while a != 0:
#     a = input("x (1 to 1024): ")
#     print(pmX.applyVoltageToDAC0to1024("DAC0",a))
#     a = input("y (1 to 1024): ")
#     print(pmX.applyVoltageToDAC0to1024("DAC1",500))
#     print(pmX.applyVoltageToDAC0to1024("DAC0",512))
#print(pmX.send_area_scan_0to1024(500,500,512,512,times=10))
pmX.send_area_scan_0to1024(300, 300, 550, 642, times=50)
print(pmX.applyVoltageToDAC0to1024("DAC1", 500))
print(pmX.applyVoltageToDAC0to1024("DAC0", 642))
