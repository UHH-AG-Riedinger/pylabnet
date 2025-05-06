import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
import numpy as np

logger = lg.LogClient()

dlc_pro = hm.autoconnect_device(device_tag='toptica_dlc_pro', logger=logger)

logger.info('DLC Connected')
b = dlc_pro.turn_on()
