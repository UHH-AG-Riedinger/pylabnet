import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm

logger = lg.LogClient()

pmX = hm.autoconnect_device(device_tag='Arduino_Galvo', logger=logger)

nktLaser = hm.autoconnect_device(device_tag='white_laser', logger=logger)
nktLaser.emission_off()#if this does not work, restart the laser device server in pylabnet

#pmX.send_area_scan_0to1024(340, 450, 782, 312, times=0)
#pmX.send_area_scan_0to1024(1024, 1024, 512, 512, times=0)
#pmX.send_area_scan_0to1024(204, 100, 822, 462, times=0)
#pmX.send_area_scan_0to1024(420, 550, 400, 730, times=0)
#420 and 550 : vetzical horizontal
print(pmX.applyVoltageToDAC0to1024("DAC1", 512))#275 x axis825
print(pmX.applyVoltageToDAC0to1024("DAC0", 780))#394 y axis#80#814

#pmX.send_area_scan_0to1024(300, 200, 730, 512, times=0)

#pmX.send_area_scan_0to1024(160, 550, 80, 575, times=0)
#pmX.send_area_scan_0to1024(420, 550, 813, 730, times=0)

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
# nktLaser = hm.autoconnect_device(device_tag='white_laser', logger=logger)
# nktLaser.emission_on()
#pmX.send_area_scan_0to1024(300, 300, 300, 242, times=50)
#print(pmX.applyVoltageToDAC0to1024("DAC1", 242))
#print(pmX.applyVoltageToDAC0to1024("DAC0", 300))
