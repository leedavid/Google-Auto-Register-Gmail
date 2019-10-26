#!/usr/bin/env python3

import math
import re
import random
import sys
import os
import subprocess
import time
import requests
from PIL import Image
from six.moves import input
import win32gui, win32ui, win32con, win32api
from common.web360 import CWEB360
import csv

def main(): 
    

    try:

        #sql = ('UPDATE tgmail set isUse = "Y", note = "%s" where id = "%d"' %('12', 32))
        '''
        dm = win32api.EnumDisplaySettings(None, 0)
        dm.PelsHeight = 1080
        dm.PelsWidth = 1920
        dm.BitsPerPel = 32
        dm.DisplayFixedOutput = 0
        win32api.ChangeDisplaySettings(dm, 0)
        '''
        print('欢迎您使用全自动 colab 训练脚本！')

        web = CWEB360()  
        
        #test(web)   

        #with open('lgl.csv') as f:   
        # 
             
     

        #web.ImportCsv2db()  
        #web.same_accound_delete()    

        web.run()
        #web.train_all()

        pass
       

    except KeyboardInterrupt:

        print('\n谢谢使用', end='')
        #hwnd = web.getHwndByUserID(UserID)
        #cap_100(web,hwnd)


    pass

def test(web):
   
    #cap_100(web, 0x00290270)  # 手工截图 100 张  

    pass

def cap_100(web, _hwnd):


    fileName = 'ZZZ'
    i = 1
    while i < 20:
        web.CaptureOne(fileName+str(i), _hwnd)
        i += 1
        pass

    


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:      
        print('\n谢谢使用')
        exit(0)