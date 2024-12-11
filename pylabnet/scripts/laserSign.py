import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm

logger = lg.LogClient()

# pmX = hm.autoconnect_device(device_tag='Arduino_Galvo', logger=logger)
# nktLaser = hm.autoconnect_device(device_tag='white_laser', logger=logger)
laserSign = hm.autoconnect_device(device_tag='Arduino_Laser_Sign', logger=logger)

# on = nktLaser.read_power()
# if on == 0:
#     laserSign.turn_off()

# for i in range(10):
#     laserSign.turn_on()
#     time.sleep(0.5)
#     laserSign.turn_off()
#     time.sleep(0.5)

laserSign.turn_off()
