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
import cv2
import numpy as np
from common.GmailSqlite import CGmailSqlite, Gmail
from common.sms51ym import SMS51ym




PIC_CAP_FORMAT = '.jpg'
PIC_SELECT_FORMAT = '.png'

class Cmygui32:
    
    def __init__(self):
        
        self._MEconsoleHwnd = -1     # 模拟器控制台
        #self._hwndMainButton = -1    # 安卓主窗口home键窗口
        self._hwndMain = -1          # 安卓主窗口  
        self.imgx = -1
        self.imgy = -1     
        self.timeBegin = time.time()   
        self.timeEnd = time.time()     

        self.getMEmuConsoleHwnd()
        self.getMEmuWinHwnd()

    # 新开一台虚拟机
    def ReBuildMachine(self):

       # 关闭当前窗口
        self.ImgShutDown()      
        time.sleep(2.0)

        # 按下删除按钮
        if self.ConsoleImgLeftClick('colone_machine_icon', self._MEconsoleHwnd, 500, 0) == False:
            return False

        time.sleep(1.0)
        # 删除确认窗口
        hyesno = self.getPopHwnd(286,167)
        if hyesno == -1:
            return False

        # 确认删除        
        if self.ConsoleImgLeftClick('colone_del_ok', hyesno, 0, 0) == False:
            return False                    

        time.sleep(2.0)         
        print('已删除虚拟机')    
        
        # 打开详细菜单
        if self.ConsoleImgLeftClick('colone_machine_CCC', self._MEconsoleHwnd, 0, 0) == False:
            return False  
        
        time.sleep(1.0)
        # 按克隆按钮
        if self.ConsoleImgLeftClick('colone_machine_clone', self._MEconsoleHwnd, 0, 0) == False:
            return False  
                            
        time.sleep(1.0)

        # 正在等待克隆完成
        while self.ConsoleImgLeftClick('colone_start_clone', self._MEconsoleHwnd, 200, 0) == False:
            print('正在等待克隆完成')   
            time.sleep(1.0)  

        # 再启动第二个
        self._hwndMain = -1
        while self._hwndMain == -1:             
            self.getMEmuWinHwnd()   
            print('正在等待窗口启动')   
            time.sleep(1.0)  

        time.sleep(1.0) 

        # 查找shadowsocks 按钮确认窗口已打开
        while self.SearchImage("shadow_shocks_icon", "shadow_ss",True) == False:
            print("wait 窗口打开完成")
            time.sleep(1.0)

        print('已启动新的窗口')
        return True       

    # 自动注册
    def AutoRegistGmail(self, _num):

        if self._hwndMain == -1:
            print("虚拟机还没有打开！")
            return

        Gsql = CGmailSqlite()    
        Gsql._tryNUm = 2

        # 准备工作
        self.Regprepare()        

        while _num > 0:

            self.timeBegin = time.time()

            print('还有 ' + str(_num) + ' 号要注册')

            Gsql.InitEmail()

            # Gsql.insertOneGmail()  # 防止中途出错
            self.RegOneGmail(Gsql)   # 注册成功      

            if Gsql._success == True:

                _num -= 1  
                self.timeEnd = time.time()

                print("成功注册一个Gmail, 用时：", self.timeEnd - self.timeBegin)
                print("Emain: ", Gsql._gmail._email + '@gmail.com')
                print("password: ", Gsql._gmail._password.lower())
                print("phone: ", Gsql._gmail._phone)
                
                Gsql._tryNUm = 2
            else:
                Gsql._tryNUm -= 1
                if Gsql._tryNUm <= 0:
                    print('注册出错了3次，重做虚拟机！')
                    if self.ReBuildMachine() == False:
                        print('重建窗口失败')
                        break
                    else:
                        print('重建窗口成功！又可以开始注册了')
                        self.Regprepare()  # 出错返回桌面，从头再来
                        Gsql._tryNUm = 2
                else:
                    self.ImgHome()
                    print('出错重试 还有 ', str(Gsql._tryNUm), " 次")
                    self.Regprepare()  # 出错返回桌面，从头再来                    

        print('本机注册完成任务！')

    # 新窗口建立后的准备工作
    def Regprepare(self):

        # 确认ss 正常
        N = 10
        while self.SearchImage("shadow_run_ok","shadow_ss",True) == False:

            if self.ImgLeftClick("shadow_shocks_icon", "shadow_ss") == True:
                print("wait shadow_shocks_icon")
          
            if self.ImgLeftClick("shadow_shocks_start", "shadow_ss") == True:
                print("wait shadow_shocks_open")

            print("wait shadow_shocks runing OK")
            time.sleep(1.0)
            N -= 1
            if N <= 0:
                self.ImgHome()   

            break 

                        

        time.sleep(1.0)        
        self.ImgHome()
        time.sleep(1.0)

        # 按下Gmail图标
        while self.ImgLeftClick("gmail_icon", "tmp") == False:
            print("finding gmail icon....")
            time.sleep(1.0)
        time.sleep(2.0)

        self._success = True

    def CommunityError(self):
        self.ImgHome()
        time.sleep(1.0)
        print("谷歌不能登录，返回处理")
        self.Regprepare()

    # 注册一个gmail 
    def RegOneGmail(self, _Gsql):    
   
        # ----------------------------------------------  
        # add email address
        EN = 20 
        while True:

            # 准备工作也可以放在这儿啊：
            
            time.sleep(0.5)
            if self.ImgLeftClick("gmail_got_it", "tmp") == True:
                print("finding gmail GOT IT....")  

            # 如果在 inbox 界面了
            time.sleep(0.5)
            if self.ImgLeftClick('gmail_index_1','tmp') == True:
                time.sleep(0.5)
                self.WinLeftClick(self._hwndMain, 50, 140) # 点击大图标
                time.sleep(0.5)
                if self.ImgLeftClick('index_add_account','tmp') == True:
                    print("finding index_add_account....") 
            
            time.sleep(0.5)
            if self.ImgLeftClick("gmail_add_acount_main", "tmp") == True:
                print("add add account main ....")
             
            time.sleep(0.5)
            if self.ImgLeftClick("gmail_add_email_address", "tmp") == True:
                print("add first email....")
                time.sleep(1.0)
                break

            time.sleep(0.5)
            # add other address 
            if self.ImgLeftClick("gmail_add_email_other_address", "tmp") == True:
                print("add another email....")
                time.sleep(1.0) 
                break

            time.sleep(0.5)
            # 如果发现的确是帐号界面，有可能是帐号过多，要下移
            if self.SearchImage('you_can_add_all_your_email', 'tmp') == True:
                win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_DOWN, 0)   
                win32api.PostMessage(self._hwndMain, win32con.WM_KEYUP, win32con.VK_DOWN, 0)  
                time.sleep(0.5)
                win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_DOWN, 0)   
                win32api.PostMessage(self._hwndMain, win32con.WM_KEYUP, win32con.VK_DOWN, 0) 
                time.sleep(0.5)

            time.sleep(0.5)
            if self.ImgLeftClick("select_gmail_icon", "tmp") == True:
                print("finding select mail ....")
                break

            time.sleep(0.5)
            if self.SearchImage('gmail_create_gmail_count','tmp') == True:
                break

            time.sleep(0.5)
            # 是不是要同步，选择不同步           
            if self.SearChImagIsSync('gmail_service_sync_1', 'tmp') == True:  
                print('不选择同步功能')
                break

            time.sleep(0.5)
            # 如果有黑屏，则点击返回            
            if self.SearchImage("is_black_screen_1", 'tmp', True) == True:
                self.Regprepare() 

            time.sleep(0.5)
            if self.SearchImage('accound_add_ok', 'tmp')  == True:
                if self.ImgLeftClick('accound_add_ok_next', 'tmp') == True:
                    print('加入帐号OK了')           
          
            print('waiting add mail menu....')

            EN -= 1
            if EN <= 0:
                self.CommunityError()
                return

        # ==============================================
        EN = 20            
        while self.ImgLeftClick('gmail_create_gmail_count','tmp') == False:
            EN -= 1
            if EN <= 0:
                self.CommunityError()
                return


            # 如果有黑屏，则点击返回            
            if self.SearchImage("is_black_screen_1", 'tmp', True) == True:
                self.ImgHome()
                print("发现黑屏，点击返回")
                self.CommunityError()
                return

            time.sleep(0.5)
            # Acccound Add 提示
            if self.SearchImage('accoun_add', 'tmp') == True:
                # click next
                if self.ImgLeftClick('accound_add_next', 'tmp') == True:
                    time.sleep(2.0)

            time.sleep(0.5)
            # 是不是要同步，选择不同步           
            if self.SearChImagIsSync('gmail_service_sync_1', 'tmp') == True:  
                print('不选择同步功能')

            time.sleep(0.5)
            # 选择 google 邮箱        
            if self.ImgLeftClick("select_gmail_icon", "tmp") == True:
                print("finding select mail ....")

            time.sleep(0.5)
            # 如果是不能登录，就要按下 home 退出
            if self.SearchImage('could_not_sign', 'tmp') == True:
                self.CommunityError()
                return

            time.sleep(0.5)
            # 如果出现了其它可用按钮，也可按下
            if self.ImgLeftClick('gmail_add_another_count','tmp') == True:
                print('gmail_add_another_count')
                break

            print('等待 核对信息...')
            time.sleep(0.5) 

        # 这儿如果有选择为自己还是孩子
        time.sleep(1.0)
        if self.SearchImage('my_or_child', 'tmp',True) == True:
            self.WinLeftClick(self._hwndMain, self.imgx, self.imgy + 5)
            print('select my_or_child ok ')    


        # 输入firstname last_name      
        while self.SearchImageAndInputName('gmail_input_name_1','tmp',
         _Gsql) == False:   

                  

            print('waiting 输入姓名...')
            time.sleep(1.0)
            # 
            if self.SearchImage('err_cannt_sign_in', 'tmp', True) == True:
                self.CommunityError()
    
        # 等待输入基本信息出现
        while True:
            self.CaptureOne('gmail_input_birth')
            if self.SearchImage('gmail_input_birth_1','gmail_input_birth') == True:
                break
            else:
                time.sleep(3.0)
                print('证明你不是机器人...')
                if self.SearchImageAndConfirmNotRobot('GetaVerification_flag','SearchImageYouNotArobot',
                    _Gsql) == True:
                    time.sleep(1.0)
                    #print('已点击 证明你不是机器人.')

                    print('输入 手机...sms')   # 可以 skip
                    if self.SearchImageAndInputSMS('enter_sms_code','gmail_input_sms',
                    _Gsql) == True: 
                        time.sleep(1.0)
                        print('已输入手机sms')
                    else:
                        return
                else:
                    if _Gsql._success == False:
                        print('不能进入基本信息输入，返回桌面')
                        time.sleep(1.0)
                        return           

      
        while self.SearchImageAndInputEmail('gmail_input_email_1','gmail_input_email',
         _Gsql) == False: 
            print('waiting 输入email...')
            time.sleep(1.0)        

            # 再输入年月日
            if self.SearchImageAndInputBirthDay('gmail_input_birth_1','gmail_input_birth',
                _Gsql) == True: 
                print('waiting 输入基本信息OK')
                time.sleep(1.0)  

       
        while self.SearchImageAndInputPassword('gmail_input_password_1','gmail_input_password',
         _Gsql) == False: 
            print('waiting 输入password...')
        
        time.sleep(1.0)     

        # 这儿不能跳过，要再次验证才行 

        N = 20
        while self.SearchImageAndPrivacy('gmail_input_Privacyterms_1','tmp',
         _Gsql) == False: 
            print('waiting Privacy Terms ！')
            time.sleep(1.0)  

            N -= 1
            while N <= 0:
                self.CommunityError()
                return


            # 再次验证手机
            if self.SearchImageAndConfirmNotRobot('is_add_phone_number','tmp',
            _Gsql, True) == True: 
                time.sleep(1.0)
                print('已输入手机号码')

                # phone_useless.png         
                if self.SearchImage('phone_useless','is_phone_ok', True) == True:
                    print("手机号不能够验证了，要换机器了")
                    _Gsql._success = False
                    _Gsql._err = '手机不能验证'
                    self.ImgHome()
                    return

                print('输入 手机...sms')   # 
                if self.SearchImageAndInputSMS('enter_sms_code','gmail_input_sms',
                    _Gsql) == False:                     
                    print('手机收不到短信！') 
                    _Gsql._success = False
                    _Gsql._err = '手机收不到短信'
                    self.ImgHome()
                    return

                    # 按下 Try agin
                    #if self.ImgLeftClick('sms_try_again', 'tmp') == True:
                    #    time.sleep(1.0)
                    #    print("再次换一个号码试试")
                    #    self.SearchImageAndConfirmNotRobot('is_add_phone_number','tmp',
                    #    _Gsql, False)

                       

        # 到这儿就成功了
        _Gsql._gmail._note = "finished"
        _Gsql.insertOneGmail()  # 注册成功保存到数据库 
       
        while self.SearchImageAndThanks('gmail_input_thanks','tmp',
         _Gsql) == False: 
            print('waiting Thanks ！')
            time.sleep(1.0)        

        print('新号注册完成！')

    # --------------
    def SearChImagIsSync(self, _Tname, _Mname):

        time.sleep(1.0)    
        if self.SearchImage(_Tname,_Mname,True) == False:
            return False

        # 查找不同步按钮      
        while self.ImgLeftClick('gmail_service_sync_not',_Mname) == False:
            time.sleep(1.0)
            print('等待点击 不同步.')

        time.sleep(1.0)
        # Accept 
        while self.ImgLeftClick('gmail_service_sync_accept',_Mname) == False:
            time.sleep(1.0)
            print('等待点击 Accept.')

    def SearchImageAndInputSMS(self, _Tname, _Mname, _Gsql):       

        while True:            
            if self.SearchImage(_Tname,_Mname,True) == True:
                time.sleep(0.5)
                break
            time.sleep(1.0)

            if self.SearchImage('phone_can_not_use', 'tmp', True) == True:
                print('此电话不能用于验证，得重来一下')
                _Gsql._success = False
                _Gsql._err = '手机不能验证'
                self.ImgHome()
                return False 

            print("等待 sms page ...")

        # 得到 code 
        _Gsql.getSms()  #  

        if _Gsql._sms._smsOK == False:
            _Gsql._success = False
            print('60秒内等到不短信')
            return False

        self.send_input_hax(_Gsql._sms._smsMessage)

        time.sleep(1.5)  

        # 按下 Next
        if self.ImgLeftClick('gmail_input_name_next_1',_Mname) == True:
            time.sleep(1.0)
            #print('已点击 Next.')
        
        return True

    def SearchImageAndPrivacy(self, _Tname, _Mname, _Gsql):
       
             
        if self.SearchImage(_Tname,_Mname,True) == False:
            time.sleep(1.0)
            #print("waiting term and privacy....")  
            return False         
        
        # 要翻到下面 VK_NEXT page down
        time.sleep(1.0)
        # win32gui.SendMessage(self._hwndMain, win32con.WM_ACTIVATE,win32con.WA_ACTIVE,0)
        # time.sleep(0.1)
        win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_NEXT, 0)
        win32api.PostMessage(self._hwndMain, win32con.WM_KEYUP, win32con.VK_NEXT, 0)

        time.sleep(1.5)

        # 按下 Next
        while self.ImgLeftClick('term_agree',_Mname) == False:           
            win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_NEXT, 0)
            win32api.PostMessage(self._hwndMain, win32con.WM_KEYUP, win32con.VK_NEXT, 0)
            print('Warting term agree botton.')
            time.sleep(1.5)

        return True

    # 手机验证
    def SearchImageAndConfirmNotRobot(self, _Tname, _Mname, _Gsql, isAgain = False):
        Gsql = _Gsql

        while True:
            self.CaptureOne(_Mname)
            if self.SearchImage(_Tname,_Mname) == False:
                return False

            time.sleep(0.5)
            # 输入手机号码  err_phone_format
            # 1. 删除原来的手机号码 WM_CHAR
            if self.SearchImage('chinese_qi',_Mname) == False:
                print("找不到中国国棋")
                return False

            time.sleep(0.5)
            x = self.imgx + 44
            y = self.imgy + 3  
            self.WinLeftClick(self._hwndMain,x,y)     
   
            time.sleep(1.0)
            win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_DELETE, 0)   
            time.sleep(2.5)     
            win32api.PostMessage(self._hwndMain, win32con.WM_KEYUP, win32con.VK_DELETE, 0)

            time.sleep(0.5)

            # 得到一个电话号码
            if isAgain == False:
                _Gsql.getPhoneNumber()
            else:
                _Gsql.GetPointPhoneNumber()

            self.send_input_hax(Gsql._gmail._phone)
            time.sleep(1.5)  

            print('input phone: ', Gsql._gmail._phone)

            # 按下 Next
            if self.ImgLeftClick('gmail_input_name_next_1',_Mname) == True:
                time.sleep(1.0)
            #print('已点击 Next.')

            elif self.ImgLeftClick('add_phnone_yes_in',_Mname) == True:
                time.sleep(1.0)
                #print('已点击 Yes Im in.')


            if self.SearchImage('phone_can_not_use', 'tmp', True) == True:
                print('此电话不能用于验证，得重来一下')
                _Gsql._success = False
                _Gsql._err = "电话不能验证"  
                self.ImgHome()  
                time.sleep(1.0)
                return False  
  
            # 再次验证电话，不需要验证了
            if isAgain == False:
                while True:            
                    if self.ImgLeftClick('verify_phone_or_cancel',_Mname) == True:
                        time.sleep(1.5)
                        return True
                    time.sleep(1.0)
                    print("等待 verify_phone_or_cancel ...")
            else:
                return True   

        return True

    # 感谢页面
    def SearchImageAndThanks(self, _Tname, _Mname, _Gsql):  
        
        if self.SearchImage(_Tname,_Mname,True) == False:
            time.sleep(1.0)
            return False

        time.sleep(1.0)           

        # 按下 Next
        while self.ImgLeftClick('gmail_input_name_next_1',_Mname) == False:
            time.sleep(1.0)
            print('waiting Thanks Next.')

        return  True
        
            
    # 输入 skip
    def SearchImageAndInputPhoneCanSkip(self, _Tname, _Mname, _Gsql):
        
        self.CaptureOne(_Mname)
        if self.SearchImage(_Tname,_Mname) == True:
            time.sleep(1.5)
        else:
            return False

        # 可以选择跳过 不用手机       
        if self.ImgLeftClick('gmail_input_phone_skip',_Mname) == True:        
            time.sleep(1.5)

        return True

    # 输入 password
    def SearchImageAndInputPassword(self, _Tname, _Mname, _Gsql):        
        
        self.CaptureOne(_Mname)
        if self.SearchImage(_Tname,_Mname) == False:
            time.sleep(1.0)
            return False

        time.sleep(1.0)            

        # 第1次口令       
        self.send_input_hax(_Gsql._gmail._password)
        time.sleep(1.0)  

        #time.sleep(0.5)
        #win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_NEXT, 0)    

        #time.sleep(0.5)
        #win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)   
        #time.sleep(0.5)
        win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)   
        time.sleep(0.1)
        win32api.PostMessage(self._hwndMain, win32con.WM_KEYUP, win32con.VK_RETURN, 0)  
        time.sleep(0.5)

        # 第2次口令 
        if self.ImgLeftClick('gmail_input_password_12',_Mname) == True:
            time.sleep(1.0)
            self.send_input_hax(_Gsql._gmail._password)
            time.sleep(2.0)
            
        # 按下 Next
        if self.ImgLeftClick('gmail_input_name_next_1',_Mname) == True:
            time.sleep(1.0)
            #print('已点击 Next.')

        print('input pass: ', _Gsql._gmail._password.lower()) 

        return True
        
    # 输入 email
    def SearchImageAndInputEmail(self, _Tname, _Mname, _Gsql):        
      
        self.CaptureOne(_Mname)
        if self.SearchImage(_Tname,_Mname) == False:
            time.sleep(1.0)
            return False

        time.sleep(1.0)            

        self.send_input_hax(_Gsql._gmail._email)
        time.sleep(0.5) 

        print('input email: ', _Gsql._gmail._email + '@gamil.com') 
        
        # 按下 Next
        if self.ImgLeftClick('gmail_input_birth_next_1',_Mname) == True:
            time.sleep(1.0)
            #print('已点击 Next.')

        return True

    # 输入 生日
    def SearchImageAndInputBirthDay(self, _Tname, _Mname, _Gsql):  
      
        self.CaptureOne(_Mname)
        if self.SearchImage(_Tname,_Mname) == False:
            time.sleep(1.0)
            return False

        time.sleep(1.5)           

        # 输入月份
        if self.ImgLeftClick('gmail_input_birth_month', _Mname, False) == True:
            time.sleep(0.5) 
            x = self.imgx + 5
            y = self.imgy + 22
            m = random.randint(0,12)
            y = y + m * 28
            self.WinLeftClick(self._hwndMain,x, y)
            time.sleep(0.5)  

            print("月份数字：", str(m))         

        time.sleep(1.0)  
        # 输入日期
        if self.ImgLeftClick('gmail_input_birth_date', _Mname, False) == True:
            time.sleep(0.5)  
            self.send_input_hax(str(_Gsql._gmail._date))
            time.sleep(0.5)  

        time.sleep(1.0)  
        # 输入年
        if self.ImgLeftClick('gmail_input_birth_year', _Mname, False) == True:
            time.sleep(0.5)  
            self.send_input_hax(str(_Gsql._gmail._year))
            time.sleep(0.5)  

        time.sleep(1.0)  
        # 输入性别
        if self.ImgLeftClick('gmail_input_birth_gender', _Mname, False) == True:
            time.sleep(1.5) 
            x = self.imgx + 100
            y = self.imgy + 15
            m = random.randint(0,4)
            y = y + m * 10
            self.WinLeftClick(self._hwndMain,x, y)
            time.sleep(1.5) 

            print("性别数字：", str(m))
        
        # 按下 Next
        if self.ImgLeftClick('gmail_input_birth_next_1',_Mname) == True:
            time.sleep(1.0)
            #print('已点击 Next.')
        
        return True

    # 输入用户名，first last name
    def SearchImageAndInputName(self, _Tname, _Mname, _Gsql):
       
        self.CaptureOne(_Mname)
        if self.SearchImage(_Tname,_Mname) == False:
            time.sleep(1.0)
            return False

        time.sleep(1.0)            

        # 输入 first name
        self.send_input_hax(_Gsql._gmail._first_name)
        time.sleep(1.0)

        #time.sleep(0.5)
        #win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_NEXT, 0)    

        #time.sleep(0.5)
        win32api.PostMessage(self._hwndMain, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)   
        time.sleep(0.1)
        win32api.PostMessage(self._hwndMain, win32con.WM_KEYUP, win32con.VK_RETURN, 0)  
        time.sleep(1.0)

        # 查找 last name pic
        if self.ImgLeftClick('gmail_input_last_name',_Mname) == True:

            # self.winRightClick(self._hwndMain, self.imgx, self.imgy)
            time.sleep(1.0)
            self.send_input_hax(_Gsql._gmail._last_name)
            time.sleep(1.5)

        # 按下 Next
        if self.ImgLeftClick('gmail_input_name_next_1',_Mname) == True:
            time.sleep(1.0)
            #print('已点击 Next.')

        return True
        
    def send_input_hax(self, msg):
        hwnd = self._hwndMain
        #win32gui.SendMessage(hwnd, win32con.WM_ACTIVATE,win32con.WA_ACTIVE,0)
        for c in msg:
            if c == "\n":
                win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32api.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                #win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                #win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            else:
                #win32api.SendMessage(hwnd, win32con.WM_CHAR, ord(c), 0)
                win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, ord(c), 0)
                #win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(c), 0)
                win32api.PostMessage(hwnd, win32con.WM_KEYUP, ord(c), 0)

     
            time.sleep(0.1)

    # 等待图片消失
    def ImgWait(self, _Tname, _Mname):
        while True:
            # 截图
            self.CaptureOne(_Mname)
            if self.SearchImage(_Tname,_Mname) == False:
                time.sleep(1.0)
                return
            
            print("waiting page finished .... sleep 1.0s >> ")
            time.sleep(1.0)

    def getPicPath(self):
        return './resource/image/'

    def getFindPath(self):
        return './resource/imagefind/'

    # 查找一个图，返回位置
    def SearchImage(self, _timgFileName, _mainImgFileName, isCap = False):

        if isCap == True:
            self.CaptureOne(_mainImgFileName)

        _timgFileName = _timgFileName + PIC_SELECT_FORMAT
        _mainImgFileName = _mainImgFileName + PIC_CAP_FORMAT

        timgpath = self.getFindPath() + _timgFileName
        template = cv2.imread(timgpath)

        # template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
        template_size = template.shape[:2]

        mFilePathName = self.getPicPath() + _mainImgFileName
        img = cv2.imread(mFilePathName)
        #img = cv2.resize(img, (0, 0), fx=scale, fy=scale)
        #img, src_x, src_y = search(img)

        #cv2.imshow('img',img)
        #cv2.imshow('template',template)
        #cv2.waitKey(0)

        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)       

        threshold = 0.90

        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            self.imgx = int(pt[0] + template_size[1] / 2)
            self.imgy = int(pt[1] + template_size[0] / 2)
            if self.imgx > 10 and self.imgy > 10:
                return True
        return False

    def WinLeftClick(self, _hwnd, _x, _y):
        client_pos = [_x, _y]
        tmp=win32api.MAKELONG(client_pos[0],client_pos[1])
        win32gui.SendMessage(_hwnd, win32con.WM_ACTIVATE,win32con.WA_ACTIVE,0)
        win32gui.SendMessage(_hwnd, win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,tmp)    
        win32gui.SendMessage(_hwnd, win32con.WM_LBUTTONUP,0,tmp)

    def winRightClick(self, _hwnd, _x, _y):
        client_pos = [_x, _y]
        tmp=win32api.MAKELONG(client_pos[0],client_pos[1])
        win32gui.SendMessage(_hwnd, win32con.WM_ACTIVATE,win32con.WA_ACTIVE,0)
        win32gui.SendMessage(_hwnd, win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,tmp)    
        win32gui.SendMessage(_hwnd, win32con.WM_LBUTTONUP,0,tmp)
    
    # 控制台点击, 要偏移一些位置
    def ConsoleImgLeftClick(self, _Tname, _hwnd, x, y):
        Mname = 'consoleTmp'
        self.CaptureOne(Mname,_hwnd)

        if self.SearchImage(_Tname, Mname) == True:
            self.WinLeftClick(_hwnd, self.imgx + x, self.imgy + y)
            return True
        return False

    # 搜索图片，并窗口点击 
    def ImgLeftClick(self,_Tname, _Mname, _Iscap=True):

        if _Iscap == True:
            self.CaptureOne(_Mname)

        if self.SearchImage(_Tname,_Mname) == True:
            # client_pos = [self.imgx, self.imgy]
            self.WinLeftClick(self._hwndMain,self.imgx, self.imgy)
            return True
        return False

    # 安卓窗口回退
    def ImgBack(self):        
        self.ImgLeftClick('back', 'tmp')

    # 安卓窗口主页
    def ImgHome(self):        
        self.ImgLeftClick('home', 'tmp')  

    def ImgShutDown(self):
        try:
            self.ImgLeftClick('shut_down','tmp') 
        except:
            pass

    # 安卓任务管理器
    def ImgTaskList(self):        
        self.ImgLeftClick('task', 'tmp')

    # 抓图一个
    def CaptureOne(self, _filename, _hwnd = 0):
        # _hwnd=0 为桌面窗口  

        _filename = _filename + PIC_CAP_FORMAT

        if _hwnd == 0:
            _hwnd = self._hwndMain    

        # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）  
        hwndDC = win32gui.GetWindowDC(_hwnd)
        # 根据窗口的DC获取mfcDC
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        # mfcDC创建可兼容的DC
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建bigmap准备保存图片
        saveBitMap = win32ui.CreateBitmap()

        # 获取窗口大小
        left, top, right, bottom = win32gui.GetWindowRect(_hwnd)
        w = right - left
        h = bottom - top

        # 为bitmap开辟空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        # 高度saveDC，将截图保存到saveBitmap中
        saveDC.SelectObject(saveBitMap)
        # 截取从左上角（0，0）长宽为（w，h）的图片
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)

        saveBitMap.SaveBitmapFile(saveDC, self.getPicPath() + _filename)

    def getPopHwnd(self,_w,_h):
        hwndList = self.get_child_windows(0)
        for hwnd in hwndList:
            try:
                className = win32gui.GetClassName(hwnd)
            
                if className == 'Qt5QWindowIcon':
                    title = win32gui.GetWindowText(hwnd)
                    if title == 'MEmuConsole':                        
                        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                        w = right - left
                        h = bottom - top
                        if w == _w and h==_h:  
                            print('发现console pop 窗口，hwnd:', hex(hwnd), ' 窗口：', str(left) + " " +
                            str(top) + " " +   str(right) + " " + str(bottom))
                            return hwnd                            
            except:
                return -1        
        return -1

    # 得到console 窗口句柄    
    def getMEmuConsoleHwnd(self):

        hwndList = self.get_child_windows(0)
        for hwnd in hwndList:
            try:
                className = win32gui.GetClassName(hwnd)
            
                if className == 'Qt5QWindowIcon':
                    title = win32gui.GetWindowText(hwnd)
                    if title == 'MEmuConsole':                        
                        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                        w = right - left
                        if w > 700:  
                            print('发现console窗口，hwnd:', hex(hwnd), ' 窗口：', str(left) + " " +
                            str(top) + " " +   str(right) + " " + str(bottom))
                            self._MEconsoleHwnd = hwnd
                            return
            except:
                pass
    
    # 得到安卓窗口句柄
    def getMEmuWinHwnd(self):
    
        Thwnd = -1
        hwndList = self.get_child_windows(0)
        for hwnd in hwndList:
            try:
                className = win32gui.GetClassName(hwnd)            
                if className == 'Qt5QWindowIcon':
                    #title = win32gui.GetWindowText(hwnd)
                    #if title == 'MEmu':
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    h = bottom - top
                    if h > 780:
                        Thwnd = hwnd
                        break   
            except:
                pass        

        if Thwnd != -1:
            left, top, right, bottom = win32gui.GetWindowRect(Thwnd)
            print('发现安卓窗口，hwnd:', hex(Thwnd), ' 窗口：', str(left) + " " +
            str(top) + " " +   str(right) + " " + str(bottom) + ' w= ' + str(right-left) 
            + " h= " + str(bottom - top))
            self._hwndMain = Thwnd
            
            """
            # FindWindowEx(hwndParent=0, hwndChildAfter=0, lpszClass=None, lpszWindow=None);
            Thwnd = win32gui.FindWindowEx(Thwnd,0,'Qt5QWindowIcon', 'MainWindowWindow')

            # 安卓主窗口home键窗口
            hwndHome = self.get_child_windows(Thwnd)
            for hwnd in hwndHome:
                className = win32gui.GetClassName(hwnd)   
                if className ==  'Qt5QWindowIcon':
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    w = right - left
                    if w == 36:
                        print('发现安卓Home键窗口，hwnd:', hex(hwnd), ' 窗口：', str(left) + " " +
                        str(top) + " " +   str(right) + " " + str(bottom) + ' w= ' + str(right-left) 
                         + " h= " + str(bottom - top))
                        self._hwndMainButton = hwnd


            Thwnd = win32gui.FindWindowEx(Thwnd,0,'Qt5QWindowIcon','CenterWidgetWindow')
            Thwnd = win32gui.FindWindowEx(Thwnd,0,'Qt5QWindowIcon','RenderWindowWindow')
            Thwnd = win32gui.FindWindowEx(Thwnd,0,'subWin','sub')
            Thwnd = win32gui.FindWindowEx(Thwnd,0,'subWin','sub')
            left, top, right, bottom = win32gui.GetWindowRect(Thwnd)
            print('发现安卓窗口，hwnd:', hex(Thwnd), ' 窗口：', str(left) + " " +
            str(top) + " " +   str(right) + " " + str(bottom) + ' w= ' + str(right-left) 
            + " h= " + str(bottom - top))
            self._hwndMain = Thwnd
            """            
        else:
            print("未发现安卓窗口")
           
    def get_child_windows(self,parent):     
        '''     
        获得parent的所有子窗口句柄
        返回子窗口句柄列表
        '''     
        #if not parent:         
        #    return      
        hwndChildList = []     
        win32gui.EnumChildWindows(parent, lambda hwnd, param: param.append(hwnd),  hwndChildList)          
        return hwndChildList 
     
    

