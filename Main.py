#!/usr/bin/env python3

import math
import re
import random
import sys
import os
import time
import requests
from PIL import Image
from six.moves import input
import win32gui, win32ui, win32con, win32api
#from Utility.Colors import DEFAULT, RED
from common.gui32 import Cmygui32


def cap_100():
    my = Cmygui32()

    fileName = 'ZZZ'
    i = 1
    while i < 20:
        my.CaptureOne(fileName+str(i))
        i += 1
        pass

# ----------------------------------------
def main():
    
    # 手工截图 100 张
    #cap_100()

    my = Cmygui32()
    my.AutoRegistGmail()
    
    # my.CaptureOne("console", my._MEconsoleHwnd)
    # my.ReBuildMachine()

    


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:      
        print('\n谢谢使用')
        exit(0)