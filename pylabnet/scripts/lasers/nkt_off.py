import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm

logger = lg.LogClient()

nktLaser = hm.autoconnect_device(device_tag='white_laser', logger=logger)

logger.info("Turning off white laser....")
nktLaser.emission_off()
