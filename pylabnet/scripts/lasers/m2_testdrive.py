# -*- coding: utf-8 -*-
from pylabnet.utils.logging.logger import LogClient, LogHandler
import pylabnet.utils.helper_methods as hm
from pylabnet.hardware.lasers.m2_solstis import Driver
from pylabnet.network.client_server.m2_solstis import Service, Client
import numpy as np


def main():

    logger = LogClient()

    tisa = hm.autoconnect_device(device_tag='m2_solstis', logger=logger)

    cv = tisa.get_voltage()
    sp = cv * 1.001
    print(f'Current voltage: {cv} V, setting to {sp} V')
    tisa.set_voltage(sp, report=True)


if __name__ == '__main__':
    main()
