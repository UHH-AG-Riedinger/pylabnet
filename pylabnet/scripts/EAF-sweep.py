import pylabnet.utils.logging.logger as lg
import pylabnet.utils.helper_methods as hm
#import pyvisa
import numpy as np

from pynput import keyboard
from pynput.keyboard import Key


logger = lg.LogClient()

pmx = hm.autoconnect_device(device_tag='EAF_Telescope', logger=logger)
#pmx.EAFmove(10000)
print(pmx.EAFget_position())


def on_key_release(key):
    if key == Key.right:
        pmx.EAFmove(pmx.EAFget_position() + 1000)
    elif key == Key.left:
        pmx.EAFmove(pmx.EAFget_position() - 1000)
    elif key == Key.up:
        print("Up key clicked")
    elif key == Key.down:
        print("Down key clicked")
    elif key == Key.esc:
        exit()


with keyboard.Listener(on_release=on_key_release) as listener:
    listener.join()
