import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
import time


logger = lg.LogClient()

galvo = hm.autoconnect_device(device_tag='Arduino_Galvo', logger=logger)
ZWOCamera = hm.autoconnect_device(device_tag='ZWOCamera', logger=logger)
nktLaser = hm.autoconnect_device(device_tag='white_laser', logger=logger)


#Name of the experiment
name = "202405010_AfterWarmup"


def take_picture(experiment_name):
    # Führen Sie hier Ihren Befehl aus
    logger.info("Starting white laser....")
    nktLaser.emission_on()

    logger.info("Starting galvo....")
    galvo.send_area_scan_0to1024(350, 600, 670, 250, times=3)
    #time.sleep(2)
    logger.info("Starting taking picture....")
    ZWOCamera.take_picture(name=experiment_name)
    #time.sleep(1)
    logger.info("Turning off white laser....")
    nktLaser.emission_off()


#set how long pictures are being taken
start_time = time.time()
end_time = start_time + 60 # 8 hours in seconds

while time.time() < end_time:
    take_picture(name)
    # Busy waiting, avoid for long running commands
    time.sleep(5)  # 600 seconds are 10 minutes


# pmX.send_area_scan_0to1024(100, 100, 642, 550, times=500)
# print(pmX.applyVoltageToDAC0to1024("DAC1", 550))
# print(pmX.applyVoltageToDAC0to1024("DAC0", 642))
