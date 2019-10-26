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
import win32gui, win32ui, win32con, win32api, win32process, win32event, pywintypes
import cv2
import numpy as np
from ctypes import windll
from common.GmailSqlite import CGmailSqlite, Gmail
import easygui
import yaml
import csv
import shutil

class CWEB360:

    PIC_CAP_FORMAT = '.jpg'
    PIC_SELECT_FORMAT = '.png'

    def __init__(self):
  
        self._config_dir = './config.yaml'

        self.cfg = yaml.safe_load(open(self._config_dir,'r').read())     

        self._webExePath = self.cfg['webExePath']
        self._userPath = self.cfg['userPath']
        self._userID = self.cfg['userID']
        self._trainID = self.cfg['trainID']

        self.err_captrue = 0
 
        self._userID_changed = True
        self._trainID_changed = True
        self._trainNum = 0

        self.imgx = -1
        self.imgy = -1     
        self.timeBegin = time.time()   
        self.timeEnd = time.time()    

        self.Hwnds360 = [-1] * int(self.cfg['maxUser'])  # 360 窗口句柄数组 
        self.Hwnds360StartTime = [-1] * int(self.cfg['maxUser'])  # 360 窗口句柄数组 

        self.SQL = CGmailSqlite(self.cfg['gmailDbName'])      


    # 析构函数
    def __del__(self):
        #self.save_yaml()
        pass

    def run(self):
        fun = self.cfg['functionSelect']
        if fun == 1:
            self.add_user()
        elif fun == 2:
            self.train_all()
        elif fun == 3:
            self.ImportCsv2db()       
        else:
            print(
                'functionSelect = 1: login \n'
                'functionSelect = 2: train\n'
                'functionSelect = 3: import account\n')
        
 
    def save_yaml(self):
        with open(self._config_dir,'w') as outfile:
            yaml.dump(self.cfg,outfile,default_flow_style=False)


    def execute (self, cmd, timeout = 0):

        if timeout == 0:
            timeout = win32event.INFINITE
			
        info = win32process.CreateProcess(None, cmd, None, None, 0, 0, None, None, win32process.STARTUPINFO())
        subprocess = info [0]    
        res = 0   
		
        rc = win32event.WaitForSingleObject (subprocess, timeout)			
		
        if rc == win32event.WAIT_FAILED:	
            return None, -1
			
        if rc == win32event.WAIT_TIMEOUT:
            try:
                win32process.TerminateProcess (subprocess, 0)					
            except:
                return None, -3
            return None, -2
		
        if rc == win32event.WAIT_OBJECT_0:
            res =  win32process.GetExitCodeProcess(subprocess) 

        return info, res
        
    # 导入帐号到数据库
    def ImportCsv2db(self):

        #with open('lglpassdb2.csv') as f:        
        #    f_csv = csv.reader(f)

        #headers = next(f_csv)   
        #result = {}
        #for item in f_csv:

        fname = self.cfg['csvFile']

        f = open(fname)
        line = f.readline()    

        while True:
            line = f.readline()  
            if not line:
                break

            line = line.strip('\n')

            item = line.split(',')

            #result[item[0]] = item[1]
            num = len(item)
            if num >= 3:
                if self.cfg['csvWithGmail'] == True:
                    email = item[0]
                else:
                    email = item[0] + '@gmail.com'
                password = item[1]
                base = item[2]  
            else:
                continue

            self.SQL._gmail._email = email
            self.SQL._gmail._password = password
            self.SQL._gmail._base_email = base

            self.SQL.insertOneGmail()

            print('insert one account ok: ', email, ' ', password, ' ' , base)        
            
  
        f.close()
       

    def getHwndByUserID(self, _userID):

        id = self.Hwnds360[_userID]        
        return id

    # 安装 谷歌助手
    def installGoogelPlug(self, hwnd):
        time.sleep(2.0)

        while self.SearchImage(hwnd,'gg_assisant_gray',_isCap=True) == True:
            print('已安装谷歌助手，等待连接中。。。')
            time.sleep(2.0)
       

        while self.SearchImage(hwnd,'gg_plug_icon',_isCap=True) == False:
            print("未安装谷歌助手！")
            time.sleep(1.0)
            # 点击新网页
            if self.ImgLeftClickByHwnd(hwnd,'360_new_page')  == True:  
                print('输入谷歌助手 url')
                url = 'http://www.ggfwzs.com\n'
                self.send_input_hax(hwnd, url)    
                time.sleep(2.0)

                if self.ImgLeftClickByHwnd(hwnd,'360_gg_219',_isCap=True,_xoff=260)  == True:  
                    print("在线安装助手中")                  

                    while self.SearchImage(hwnd,'gg_plug_icon',_isCap=True) == False:
                        print('已点击安装，正在等待确认中...')
                        time.sleep(1.0)

                        # 查找跳出的窗口
                        hwndList = self.get_child_windows(0)
                        for hwndgg in hwndList:
                            try:
                                className = win32gui.GetClassName(hwndgg)            
                                if className == 'Chrome_WidgetWin_2':

                                    # 得到窗口大小 
                                    
                                    _, top, _, bottom = win32gui.GetWindowRect(hwndgg)
                                    h = bottom - top
                                    if h == 237:
                                        print('find windows: ', hex(hwndgg))
                                        

                                        #win32api.PostMessage(hwndgg, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                                        #win32api.SendMessage(hwndgg, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                                        #pass
                                        # 点击添加
                                        if self.ImgLeftClickByHwnd(hwndgg,'360_gg_add_verify','are_u_want_ggzs', _isCap=False)  == True:  
                                            print("谷歌助手已安装")
                                            time.sleep(1.5)
                                            break   
                                                                     

                            except:
                                pass

        # 关闭谷歌助手已安装的页面
        while self.SearchImage(hwnd,'360_close_page_blue', _isCap=True) == True:   
            
            if self.SearchImage(hwnd,'new_page_blue') == True:
                break
            self.WinLeftClick(hwnd,self.imgx,self.imgy) 

        print('已安装谷歌助手了')
      
 
    # 关闭其它页面
    def close_all_page(self,hwnd):


        while True:
            title = win32gui.GetWindowText(hwnd)

            if len(title) < 2:
                break

            if title.find('新标签页') == 0:
                break

            if self.ImgLeftClickByHwnd(hwnd,'360_close_page_blue') == True:
                time.sleep(0.5)

        '''
        if self.SearchImage(hwnd,'360_no_ask_default',_isCap=True)  == True:           
            print('关闭缺省设置')
            time.sleep(1.0)  

        left, _, right, _ = win32gui.GetWindowRect(hwnd)
        w = right - left
        while self.SearchImage(hwnd,'360_close_page_gray', _isCap=True) == True:
            if self.imgx < w - 100:  # 
                self.WinLeftClick(hwnd,self.imgx,self.imgy)

        
        while True:
            if self.SearchImage(hwnd,'360js_new_page', _isCap=True) == True:
                if self.imgx < 200:
                    print('已清除所有的窗口了')
                    break
            if self.ImgLeftClickByHwnd(hwnd,'360_close_page_blue') == True:
                time.sleep(1.0)
        '''


        # 蓝色的关到只有新标签页

        '''
        if self.SearchImage(hwnd,'360_close_page_blue', _isCap=True) == True:
            if self.imgx < w - 100 and self.imgx > 350:
                self.WinLeftClick(hwnd,self.imgx,self.imgy) 

        # 关闭首页  
        if self.SearchImage(hwnd,'360_welcome_use',_isCap=True)  == True:
            self.ImgLeftClickByHwnd(hwnd,'360_close_page_blue')  
            print('关闭360初始页面1')
            time.sleep(1.0)

        
        if self.SearchImage(hwnd,'360_navi_new_gen',_isCap=True)  == True:
            self.ImgLeftClickByHwnd(hwnd,'360_close_page_blue')  
            print('关闭360初始页面2')
            time.sleep(1.0)

        '''


    def loging_gmail_10(self, _userID):

        hwnd = self.getHwndByUserID(_userID)

        time.sleep(1.0)
        
        self.installGoogelPlug(hwnd)  # 安装谷歌助手

        # 关闭所有的页面
        self.close_all_page(hwnd)

        if self.ImgLeftClickByHwnd(hwnd,'360_input_url')  == True:           
            print('输入url')
            time.sleep(0.5)    

        url = self.cfg['ColabUrl'] + '\n'
        self.send_input_hax(hwnd, url)    
        time.sleep(2.0)
        
        # 等待输入 email

        self.input_email_address(hwnd)
        self.input_email_password(hwnd)


    def input_email_address(self,hwnd):

        
        INPUT_URL = False
        ClICK_LINK = False    
        #INPUT_URL = False  
        time.sleep(1.0)
        t =  0  
        while self.SearchImage(hwnd,'gmail_forget_your_password',_isCap=True) == False:  

            if self.err_captrue > 0:
                self.err_captrue = 0                                
                return False    

            print('正在等待输入 gmail ... ID: ' + str(self._userID) + ' t=' + str(t))
            t += 1
            if t > self.cfg['inputGmailTryTimes']:
                return False

            if self.SQL.GetOneUnunsedEmail() == False:
                print('数据库中已没有未使用用户了！')
                return False

            #if self.SearchImage(hwnd,'account_is_up_limit') == True:
            #    return False
            #if self.SearchImage(hwnd,'account_is_up_limit_en') == True:
            #    return False
            if self.SearchImage(hwnd,'colab_favorite_ok') == True:
                return False

            if self.SearchImage(hwnd,'email_too_long') == True:
                if self.ImgLeftClickByHwnd(hwnd,'icon_fresh')  == True:  
                    print('email_too_long 刷新！') 

            # 当前已登录了
            if self.SearchImage(hwnd,'colab_play_ground') == True or self.SearchImage(hwnd,
            'colab_play_ground_2') == True:
                if self.ImgLeftClickByHwnd(hwnd,'gmail_let_loggin')  == False:
                    return True
                else:
                    time.sleep(3.0)
                    # 可以另存为副本了

            if INPUT_URL == False:    
                if self.ImgLeftClickByHwnd(hwnd,'360_input_url')  == True:           
                    print('输入url')
                    time.sleep(0.5)    

                if self.SearchImage(hwnd,'user_your_gmail') == True:
                    INPUT_URL = True
                    continue

                
                url = self.cfg['ColabUrl'] + '\n'
                self.send_input_hax(hwnd, url)    
                time.sleep(1.0)
                INPUT_URL = True

            #if self.SearchImage(hwnd,'360_new_page_no_url') == True:
            #    INPUT_URL = False
            
            if self.SearchImage(hwnd,'js360_err_need_reflash')  == True:  
                if self.ImgLeftClickByHwnd(hwnd,'js360_err_need_reflash')  == True:  
                    print('访问网页出错，刷新！')

            if self.SearchImage(hwnd,'err_we_all_know')  == True:  
                if self.ImgLeftClickByHwnd(hwnd,'icon_fresh')  == True:  
                    print('访问网页出错: Thats all we know 刷新！') 

            if self.SearchImage(hwnd,'err_email_adress_cannot_javascrip') == True:
                if self.ImgLeftClickByHwnd(hwnd,'360_close_page_blue') == True:
                    time.sleep(1.0)
                    print('err_email_adress_cannot_javascrip')

            # 输入太多的错误了
            if self.SearchImage(hwnd,'err_email_input_your_hear') == True:  
                self.ImgLeftClickByHwnd(hwnd,'360_close_page_blue')              
                return False
            

            if ClICK_LINK == False:
                # 有登录按钮
                if self.ImgLeftClickByHwnd(hwnd,'gmail_let_loggin')  == True: 
                    print('已点击登录')
                    time.sleep(1.0)
                    ClICK_LINK = True
                
                ## 点击添加用户，右侧的图标
                #if self.ImgLeftClickByHwnd(hwnd,'share_link',_isCap=False,_xoff=80) == True:
                #    time.sleep(1.0)
                #    if self.ImgLeftClickByHwnd(hwnd,'share_link_add_zh', _isCap=True) == True:
                #        print('已点击添加用户')
                #        time.sleep(1.0)
                #        ClICK_LINK = True   
            
            if self.SearchImage(hwnd,'very_satisfied') == True:
                if self.ImgLeftClickByHwnd(hwnd,'very_satisfied') == True:
                    print('非常满意')
                    time.sleep(1.5)
                if self.ImgLeftClickByHwnd(hwnd,'very_satisfied_skip') == True:
                    print('非常满意, skip quesiton') 

            if self.SearchImage(hwnd,'gmail_creat_your_count') == True:            
                if self.ImgLeftClickByHwnd(hwnd,'gmail_login_email') == True:
                    time.sleep(0.5)

                if self.SearchImage(hwnd,'empty_email',_isCap=True) == True or self.SearchImage(hwnd,
                'empty_email_2',_isCap=True) == True:
                    email = self.SQL._gmail._email
                    self.send_input_hax(hwnd, email + '\n')
                    print('enter email:', email)                
                    time.sleep(1.0)
            
            # 如果是请输入有效的电子邮件            
            if self.SearchImage(hwnd,'gmail_is_invalid', _isCap=True) == True:   
                print('此帐号无效，从数据库中删除!')
                info = ('email: ' + self.SQL._gmail._email + '\n'
                'pass: ' + self.SQL._gmail._password + '\n'
                'phone ' + self.SQL._gmail._phone )
                print(info)
                self.SQL.DeleteEmailByBan()
                # 把这个窗口关闭，
                if self.ImgLeftClickByHwnd(hwnd,'360_close_page_blue') == True:
                    time.sleep(0.5)
                return False        

            time.sleep(1.0)

        print('已输入有效地址：', self.SQL._gmail._email)
        return True
        
    def err_mail_or_password(self,hwnd, reason):

        print(reason)
        
        info = (reason + '\n' 
            'email: ' + self.SQL._gmail._email + '\n'
            'pass: ' + self.SQL._gmail._password + '\n'
            'phone ' + self.SQL._gmail._phone )

        print(info)

        if self.cfg['deleteWarning'] == True:

            yesorno = easygui.ynbox(info,'出错了啦')
            if yesorno == True:
                self.SQL.DeleteEmailByBan()
            else:
                pass  #
        else:
            self.SQL.DeleteEmailByBan()

        # 关闭本页面
        # 把这个窗口关闭，
        if self.ImgLeftClickByHwnd(hwnd,'360_close_page_blue') == True:
            time.sleep(1.0)

   
    def input_email_password(self,hwnd):

        # 等待输入 password
        t = 0
        while self.SearchImage(hwnd,'colab_left_side',_isCap=True) == False:  

            print('正在等待输入 password... ID: ' + str(self._userID) + ' t=' + str(t))
            t += 1
            if t > self.cfg['inputGmailTryTimes']:
                return False   

            if self.err_captrue > 0:
                self.err_captrue = 0                                
                return False       

            # 输入太多的错误了
            if self.SearchImage(hwnd,'err_email_input_your_hear') == True:  
                self.ImgLeftClickByHwnd(hwnd,'360_close_page_blue')              
                return False

            if self.SearchImage(hwnd,'now_lookuping_and_down') == True:
                if self.ImgLeftClickByHwnd(hwnd,'colab_down_arrow') == True:
                    print('放下菜单项目')

            if self.SearchImage(hwnd,'err_password_changed') == True:
                self.err_mail_or_password(hwnd,'此帐号密码已更改，要从数据库中删除吗')          
                return False

            # 不再显示 安全保存 密码
            if self.ImgLeftClickByHwnd(hwnd,'gmail_not_save_password') == True:
                print('不再显示 安全保存 密码')
                time.sleep(0.5)

            # 加载笔记本出错
            if self.SearchImage(hwnd,'err_while_loading_juyper') == True:
                return False

            if self.SearchImage(hwnd,'cannt_find_notebook') == True: 
                return False

            # 输入成功了！
            if self.SearchImage(hwnd,'gmail_keep_your_safety') == True:
                if self.ImgLeftClickByHwnd(hwnd,'gmail_keep_your_safety_ok') == True:
                    return True

            # 如果再出现 playground， 就是表示登录成功了
            if self.SearchImage(hwnd,'gmail_playgroudn_again') == True:
                return True
           
            if self.ImgLeftClickByHwnd(hwnd,'gmail_forget_your_password',_xoff=-200) == True:
                time.sleep(0.5)
                passw = self.SQL._gmail._password
                self.send_input_hax(hwnd, passw + '\n')
                print('enter password:', passw)                
                time.sleep(1.0)   

            # 如果是显示帐号已停用            
            if self.SearchImage(hwnd,'your_acc_is_ban', _isCap=True) == True:                
                self.err_mail_or_password(hwnd,'此帐号已停用，要从数据库中删除吗')
                return False

            # 此帐号需要验证
            if self.SearchImage(hwnd,'verify_your_identify',_isCap=True) == True or self.SearchImage(hwnd,
            'verify_your_identify_2') == True or self.SearchImage(hwnd,
            'verify_your_identify_3') == True:

                tv = 0
                while True:   

                    if self.err_captrue > 0:
                        self.err_captrue = 0
                        return False

                    if self.ImgLeftClickByHwnd(hwnd,'verify_by_exmail',_isCap=True) == True:
                        print('通过辅助邮箱来验证')
                        time.sleep(2.0)

                    if self.ImgLeftClickByHwnd(hwnd,'input_exmail',_isCap=False) == True:
                        print('点击输入辅助邮箱')

                    if self.ImgLeftClickByHwnd(hwnd,'input_exmail_2',
                    _isCap=False) == True or self.ImgLeftClickByHwnd(hwnd,'input_exmail_3',
                    _isCap=False) == True:
                        print('输入辅助邮箱')
                        exmail = self.SQL._gmail._base_email
                        self.send_input_hax(hwnd, exmail+"\n")

                    print('正在验证帐号... ID: ' + str(self._userID) + ' tv=' + str(tv))
                    tv += 1
                    if tv > self.cfg['inputGmailTryTimes']:
                        return False  
                 
                    # 确认您的辅助电话号码
                    if self.SearchImage(hwnd,'your_supplied_phone') == True:
                        if self.ImgLeftClickByHwnd(hwnd,'your_supplied_phone_number') == True:
                            phone = '+86' + self.SQL._gmail._phone + '\n'
                            print('input phone: ', phone)
                            time.sleep(0.2)
                            self.send_input_hax(hwnd, phone)
                            time.sleep(0.5)

                    elif self.ImgLeftClickByHwnd(hwnd,'via_phone_number') == True:
                        phone = '+86' + self.SQL._gmail._phone + '\n'
                        print('input phone: ', phone)
                        time.sleep(0.2)
                        self.send_input_hax(hwnd, phone)
                        time.sleep(0.5)

                    elif self.ImgLeftClickByHwnd(hwnd,'via_sms') == True:  # 接收短信验证
                        old_number = self.SQL._gmail._phone
                        if self.SQL.GetPointPhoneNumber() == False:
                            self.err_mail_or_password(hwnd,'这个号码不在平台上，要从数据库中删除吗')
                            return False

                    # 得到 code 
                        self.SQL.getSms()  #  
                        if self.SQL._sms._smsOK == False:
                                self.SQL._success = False                                
                                self.err_mail_or_password(hwnd,'60秒内等到不短信，要从数据库中删除吗')
                                return False
                        self.send_input_hax(hwnd, self.SQL._sms._smsMessage + '\n')
                        time.sleep(1.0)

                    elif self.SearchImage(hwnd,'please_input_your_phone') == True:
                        if self.SQL.GetPointPhoneNumber() == False:
                            self.err_mail_or_password(hwnd,'这个号码不在平台上，要从数据库中删除吗')
                            return False
                        phone = '+86' + self.SQL._gmail._phone + '\n'
                        print('input phone: ', phone)
                        time.sleep(0.2)
                        self.send_input_hax(hwnd, phone)
                        time.sleep(0.5)

                    if self.SearchImage(hwnd,'please_input_sms') == True:
                        # 得到 code 
                        self.SQL.getSms()  #  

                        if self.SQL._sms._smsOK == False:
                            self.SQL._success = False
                            print('60秒内等到不短信')
                            return False

                        self.ImgLeftClickByHwnd(hwnd,'please_input_sms_word')

                        self.send_input_hax(hwnd, self.SQL._sms._smsMessage + '\n')
                        time.sleep(0.5)  


                    if self.SearchImage(hwnd,'please_supply_phone_go_on') == True:
                        if self.SQL.GetPointPhoneNumber() == False:
                            self.err_mail_or_password(hwnd,'这个号码不在平台上，要从数据库中删除吗')
                            return False
                        phone = '+86' + self.SQL._gmail._phone + '\n'
                        print('input phone: ', phone)
                        time.sleep(0.2)
                        self.send_input_hax(hwnd, phone)
                        time.sleep(0.5)

                    if self.SearchImage(hwnd,'get_sms_code') == True:
                        # 输入电话号码
                        old_number = self.SQL._gmail._phone
                        if self.SQL.GetPointPhoneNumber() == False:
                            self.err_mail_or_password(hwnd,'这个号码不在平台上，要从数据库中删除吗')
                            return False

                        ph = '+86' + old_number + '\n'
                        self.send_input_hax(hwnd, ph)
                        pass

                    if self.ImgLeftClickByHwnd(hwnd,'gmail_phone_detail_info') == True: 
                        pass

                    
                    if self.SearchImage(hwnd,'gmail_is_stopped') == True:  # 此帐号已停用
                        self.err_mail_or_password(hwnd,'此帐号已停用，要从数据库中删除吗')
                        return False

                    if self.SearchImage(hwnd,'gmail_is_stopped_2') == True:  # 此帐号已停用
                        self.err_mail_or_password(hwnd,'此帐号已停用，要从数据库中删除吗')
                        return False                    
 

                    # 登录成功，找不到笔记本
                    if self.SearchImage(hwnd,'cannt_find_notebook') == True:                                                
                        break
                    if self.SearchImage(hwnd,'err_load_notebook') == True:                        
                        break   

                    if self.ImgLeftClickByHwnd(hwnd,'no_save_password') == True:
                        print('此网站一律不保存密码!')

                    if self.SearchImage(hwnd,'colab_left_side') == True:
                        break    
               

            # 此网页为英语，是否需要翻译，关了再说
            if self.SearchImage(hwnd,'360js_us_youdao',_isCap=True) == True: 
                if self.ImgLeftClickByHwnd(hwnd,'360js_us_youdao_close') == True:
                    print('关闭翻译选项')             
         

        return True


    def colab_add_to_favorite(self,hwnd):

        CLEAR = False
        INPUT_URL = False   
        CLICK_5 = False
        # 查找是不是已加入了:
        while True:
            print('正在收藏colab... ID: ' + str(self._userID))   

            if self.SearchImage(hwnd,'colab_favorite',_isCap=True) == True:
                print('已加入收藏夹了')
                return True

            if self.ImgLeftClickByHwnd(hwnd,'err_page_white_favorite')  == True: 
                print('访问出错，刷新一下') 

            if self.SearchImage(hwnd, 'that_all_we_know') == True:
                print('that all we know, fresh again')
                if self.ImgLeftClickByHwnd(hwnd,'icon_fresh') == True:
                    time.sleep(1.0)
                

            if CLEAR == False:
                # 关闭所有的页面
                self.close_all_page(hwnd)
                CLEAR = True

            if INPUT_URL == False:    
                if self.ImgLeftClickByHwnd(hwnd,'360_input_url')  == True:           
                    print('输入url')
                    time.sleep(0.5)    

                url = self.cfg['ColabUrl'] + '\n'
                self.send_input_hax(hwnd, url)    
                time.sleep(1.0)
                INPUT_URL = True

            if CLICK_5 == False:
                if self.SearchImage(hwnd,'colab_play_ground') == True:
                    # 点击收藏夹
                    if self.ImgLeftClickByHwnd(hwnd,'js360_favorite_icon') == True:
                        print('点击收藏五角星')
                        CLICK_5 = True
                        time.sleep(0.5)

            #if self.ImgLeftClickByHwnd(hwnd,'js360_favorite_yes', '360js_favorite_ok', _isCap=False) == True:
            #    print('点击收藏 确认')

            # 查找跳出的窗口
            hwndList = self.get_child_windows(0)
            for hwndgg in hwndList:
                try:
                    className = win32gui.GetClassName(hwndgg)            
                    if className == 'Chrome_WidgetWin_2':

                        # 得到窗口大小 
                        _, top, _, bottom = win32gui.GetWindowRect(hwndgg)
                        h = bottom - top
                        if h == 451:
                            print('find windows: ', hex(hwndgg))

                            win32api.PostMessage(hwndgg, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                            time.sleep(0.05)
                            win32api.SendMessage(hwndgg, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                            time.sleep(0.5)
                            break

                            # 点击添加
                            #if self.ImgLeftClickByHwnd(hwndgg,'js360_favorite_yes', '360js_favorite_ok', _isCap=False) == True:
                            #    print('点击收藏 确认 x: ' + str(self.imgx) + ' y: ' + str(self.imgy))
                            #    time.sleep(1.0)                                                                    

                except:
                    pass
 
    # 训练一个帐号
    def train_one_user(self, hwnd):

        # 1，判定是不是有收藏夹了
        self.close_all_page(hwnd)  # 关闭所有的页面
        if self.SearchImage(hwnd,'colab_favorite_2piece',_isCap=True) == False:  
            cmd = self._webExePath + ' "--user-data-dir=' + self._userPath + '/GGcolab' + str(self._userID) + '"'          
            self.train_one_ok(hwnd,'colab 地址未收藏: ' + cmd,isClose=True)
            return False
        
        CLICK = False
        t = 0
        while True: 

            if self.err_captrue > 0:
                self.train_one_ok(hwnd, '跑谱 err_captrue>1！',isClose=True)
                self.err_captrue = 0     
                return False           

            if t % 5 == 0:
                print('帐号：' + str(self._trainID) + ' 当前共有：'+ str(self._trainNum) + ' 帐号在运行, 正在确认当前窗口跑谱是否正常...: ' + str(t))
            t += 1   
            

            if self.SearchImage(hwnd,'connect_gray',_isCap=True):
                if self.ImgLeftClickByHwnd(hwnd,'play_gray') == True:
                    print('按下play [] 开始跑谱')
                    time.sleep(1.0)
                elif self.ImgLeftClickByHwnd(hwnd,'play_gray_kuang') == True:
                    print('按下play > 开始跑谱')
                    time.sleep(1.0)

            if t > 50:
                if self.SearchImage(hwnd,'is_loading_now') == True:                
                    if self.ImgLeftClickByHwnd(hwnd,'reflash_by_loading') == True:
                        print('正在加载...')
                        t = 10

            # 点击第二个图标
            if CLICK == False:
                if self.ImgLeftClickByHwnd(hwnd,'colab_favorite_2piece',_isCap=False) == True:
                    CLICK = True  
                    time.sleep(1.0) 

            if self.ImgLeftClickByHwnd(hwnd,'colab_play_red',_isCap=False) == True:
                print('按下了红色运行按钮')

            if self.SearchImage(hwnd,'err_load_note') == True or self.SearchImage(hwnd,
            'err_load_note2') == True:
                if self.ImgLeftClickByHwnd(hwnd,'js360_reflash') == True:
                    print('加载页面出错，刷新一下')
                    t = 10
                    time.sleep(5.0)

            if self.SearchImage(hwnd,'err_cannot_send_message') == True:
                if self.ImgLeftClickByHwnd(hwnd,'err_cannot_send_message_ok',_isCap=False) == True:
                    print('未能执行单元格。无法向运行时发送执行消息')
                    t = 10 

            if t > self.cfg['trainErrTryTimes']:                                  
                self.train_one_ok(hwnd, '训练加载页面超时了，跳过这个帐号！',isClose=True)
                return False

            if t > 30:
                if self.SearchImage(hwnd,'success_upload_game') == True:
                    self.train_one_ok(hwnd, '已开始跑谱了！',isClose=False)
                    return True  

            
            if self.ImgLeftClickByHwnd(hwnd,'very_satisfied',_isCap=False) == True:
                time.sleep(1.0) #skip_question
                if self.ImgLeftClickByHwnd(hwnd,'skip_question') == True:
                    print('skip_question') 

            
            if self.SearchImage(hwnd,'bestmove_channel_err') == True:
                self.train_one_ok(hwnd, 'Error bestmove channel closed!',isClose=True)
                return False 

            if t > 10:
                if self.SearchImage(hwnd,'received_message_to_end') == True:                
                    self.train_one_ok(hwnd, '现在正在比赛，暂停训练！！',isClose=True)
                    tk = 60*2
                    while True:
                        time.sleep(5.0)
                        print('现在正在比赛, 训练暂停：' + str(tk) + '秒')
                        tk -= 5
                        if tk <= 0:
                            break
                    return False

            if self.SearchImage(hwnd,'err_no_gpu') == True:
                self.train_one_ok(hwnd, '此帐号暂时，无法分配GPU：' + str(self._trainID),isClose=True)
                return False 
                
                #print('训练分配不到GPU，请检查设置是否有错！')
                #easygui.msgbox('训练分配不到GPU，请检查设置是否有错', 'Attention')
                #pass


                #self.train_one_ok(hwnd, '训练分配不到GPU，请检查设置！',isClose=True)
                #return False
            
            if t > self.cfg['trainRunConfirm']:
                if self.SearchImage(hwnd,'sever_busy_now') == True:                                                                   
                    self.train_one_ok(hwnd, '已开始跑谱了！',isClose=False)
                    return True

            if self.SearchImage(hwnd,'err_page_visit',_isCap=True):
                if self.ImgLeftClickByHwnd(hwnd,'err_page_visit_reflash') == True:
                    print('err_page_visit')
                    t = 10
                    time.sleep(5.0)

            if self.SearchImage(hwnd,'no_backend') == True:
                self.train_one_ok(hwnd, '此帐号暂时，无法分配GPU：' + str(self._trainID),isClose=True)
                return False           


    def train_one_ok(self, hwnd, info, isClose):
        print(info)
        self._trainID_changed = True
        self._trainID += 1

        self.cfg = yaml.safe_load(open(self._config_dir,'r').read())   
        self.cfg['trainID'] = self._trainID
        self.save_yaml()

        if isClose == False:
            # 再把窗口最小化，不然会用3D加速
            if self.ImgLeftClickByHwnd(hwnd,'win_mini_hide') == True:
                print('窗口最小化，防止启用3D加速')
        else:
            print('此没有跑谱，为节省内存，关闭窗口！')
            win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)                
            win32gui.SendMessage(hwnd, win32con.WM_CLOSE,0,0)

            if self.ImgLeftClickByHwnd(hwnd,'js360_close',_xoff=25) == True:
                time.sleep(1.0)
                self._leave_360() 


    def _leave_360(self):
        # 查找跳出的窗口
        hwndList = self.get_child_windows(0)
        for hwndgg in hwndList:
            try:
                className = win32gui.GetClassName(hwndgg)            
                if className == 'Chrome_WidgetWin_2':                                  
                                    
                    #_, top, _, bottom = win32gui.GetWindowRect(hwndgg)
                    #h = bottom - top
                    #if h == 237:
                    #    print('find windows: ', hex(hwndgg))                                        

                    win32api.PostMessage(hwndgg, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                    win32api.SendMessage(hwndgg, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                                        #pass
                                        # 点击添加
                        #if self.ImgLeftClickByHwnd(hwndgg,'360_gg_add_verify','are_u_want_ggzs', _isCap=False)  == True:  
                        #    print("谷歌助手已安装")
                        #    time.sleep(1.5)
                        
                    break   
                                                                     

            except:               
                pass

    def _close_last_batch_hwnd(self):
        hwndList = self.get_child_windows(0)
        for hwnd in hwndList:
            try:
                className = win32gui.GetClassName(hwnd)            
                if className == 'Chrome_WidgetWin_1':
                    
                    title = win32gui.GetWindowText(hwnd)
                    
                    if title.find('“GGzero') != -1 or title.find('极速') != -1:  
                        
                        win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)                
                        win32gui.SendMessage(hwnd, win32con.WM_CLOSE,0,0)

                        if self.ImgLeftClickByHwnd(hwnd,'js360_close',_xoff=25) == True:
                            time.sleep(1.0)
                            self._leave_360()                                                                 

            except:
                pass

    def train_close_by_timeup(self):

        trainRestTime = self.cfg['trainRestTime'] 
        TotaluserID = self.cfg['userID']           # 总的用户数

        for i in range(1,TotaluserID):
            hwnd = self.Hwnds360[i]
            timeBegin = self.Hwnds360StartTime[i]
            if timeBegin != -1:
                timeEnd = time.time()
                restTime = (timeBegin + trainRestTime) - timeEnd
                if restTime <= 0:
                    self.Hwnds360StartTime[i] = -1

                    try:
                        win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)                
                        win32gui.SendMessage(hwnd, win32con.WM_CLOSE,0,0)
                        time.sleep(0.5)
                        if self.ImgLeftClickByHwnd(hwnd,'js360_close',_xoff=25) == True:
                            time.sleep(1.0)
                            self._leave_360() 
                    except:
                        pass
                    self._trainNum -= 1

    def train_all(self):

        close360whenStart = self.cfg['close360whenStart']
        if close360whenStart == True:
            self._close_last_batch_hwnd()   
        
        self._trainID = self.cfg['trainID']
        TotaluserID = self.cfg['userID']           # 总的用户数  
        trainMaxWindows = self.cfg['trainMaxWindows']

        start = time.time()
        while True: 
            # 训练号到了未尾
            if self._trainID > TotaluserID:                
                self.cfg = yaml.safe_load(open(self._config_dir,'r').read()) 

                self._trainID = 1 
                self.cfg['trainID'] = self._trainID
                self.save_yaml()

            # 帐号间隔                 
            time.sleep(1.0)
            print('已运行：' + str(int(time.time() - start)) + ' 秒, 当前共有：' + str(self._trainNum) + ' 帐号在运行...')

            if self._trainNum > trainMaxWindows:
                print('当前训练窗口已达到最大设定值：' + str(self._trainNum), ' 正在等待帐号训练完成...')
                self.train_close_by_timeup()  
                time.sleep(5.0)              
                continue

            if self.Hwnds360StartTime[self._trainID] == -1:
                if self._trainID_changed == True:  
                    # 打开新窗口
                    if self.openWebByUserID(self._trainID) == False:
                        print('打开极速360程序失败！')
                        return False

                    hwnd = self.getHwndByUserID(self._trainID)  
                    self._trainID_changed = False
            
            
                print('正在训练第：' + str(self._trainID) + ' 帐号')
                if self.train_one_user(hwnd) == True:
                    self.Hwnds360StartTime[self._trainID-1] = time.time()
                    self._trainNum += 1
                else:
                    self.Hwnds360StartTime[self._trainID-1] = -1                    

            else:
                print('当前帐号正在训练中... :' + str(self._trainID))
                self._trainID += 1

            self.train_close_by_timeup()

    # 删除相同的帐号
    def same_accound_delete(self):
        TotaluserID = self.cfg['userID']           # 总的用户数
        uID = self.cfg['SameIDstart']  
        lastID = uID
        while True:
            if uID >= TotaluserID:
                print('相同帐号检查完毕')
                break

            # 打开一个帐号       
            if self.openWebByUserID(uID) == False:
                ('打开极速360程序失败！')
                return False

            hwnd = self.getHwndByUserID(uID) 
            cmd = self._webExePath + ' "--user-data-dir=' + self._userPath + '/GGcolab' + str(uID) 
            print('当前帐号：' + cmd) 

            # 看有没有收藏夹了
            self.close_all_page(hwnd)  # 关闭所有的页面
            if self.SearchImage(hwnd,'colab_favorite_2piece',_isCap=True) == False:  
                      
                self.train_one_ok(hwnd,'colab 地址未收藏: ' + cmd,isClose=True)
                uID += 1
                continue

            if self.ImgLeftClickByHwnd(hwnd,'colab_favorite_2piece') == True:
                print('点击收藏夹成功')
                while True:
                    print('等待当前图标')
                    time.sleep(1.0)
                    if self.SearchImage(hwnd,'colab_share',_isCap=True) == True:
                        print('已打开colab窗口')

                        left = self.imgx + 40
                        top = self.imgy - 25
                        right = left + 50
                        bottom = top + 50

                        if lastID != uID and self.SearchImage(hwnd,'last_icon', _threshold=0.99) == True:
                            print('发现相同帐号登录了！')
                            # 关闭窗口，删除这个目录
                           
                            self.CaptureOneNotryRect('last_icon',hwnd,left,top,right,bottom)
                            edir = self.cfg['webUserPath'] + '/GGcolab' + str(uID) 
                            print(edir)

                            self.openWebByUserID(lastID)
                            hwndold = self.getHwndByUserID(lastID)  
                            self.ImgLeftClickByHwnd(hwndold,'colab_favorite_2piece')

                            info = '发现帐号重复登录了，请确认后，删除其中一个\n nowID ' + str(uID) + ' lastID: ' + str(lastID)
                            print(info)
                            
                            yesorno = True
                            if self.cfg['SameIDstartConfirm'] == True or (uID - lastID) > 4:
                                yesorno = easygui.ynbox(info,'出错了啦')

                            win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)                
                            win32gui.SendMessage(hwnd, win32con.WM_CLOSE,0,0)  
                            win32gui.ShowWindow(hwndold,win32con.SW_RESTORE)                
                            win32gui.SendMessage(hwndold, win32con.WM_CLOSE,0,0)  

                            if yesorno == True:                                     
                                time.sleep(2.0)                                
                                shutil.rmtree(edir) #将整个文件夹删除   
                            else:
                                lastID = uID   
                            uID += 1  
                            break                 
                        
                        # 再次保存本次ICON                      
                                                 
                        self.CaptureOneNotryRect('last_icon',hwnd,left,top,right,bottom)
                        win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)                
                        win32gui.SendMessage(hwnd, win32con.WM_CLOSE,0,0)
                        lastID = uID
                        uID += 1
                        break
                   
                continue
    

    # 增加一个帐号到数据库
    def gui_add_mail(self):
        pass

    def add_one_user(self, hwnd):   

        '''
        在当前窗口登录一个用户
        '''

        time.sleep(1.0)
        
        usZS = self.cfg['useGGFKZS']

        if usZS == True:
            self.installGoogelPlug(hwnd)  # 安装谷歌助手  

        # self.colab_add_to_favorite(hwnd)  # 将 colab 网址添加到收藏夹 不收藏了
       
        while True:

            if self.SearchImage(hwnd,'colab_favorite_ok', _isCap=True) == True:
                # 关闭浏览器
                #if self.SearchImage(hwnd,'360js_close') == True:           
                #    self.WinLeftClick(hwnd,self.imgx,self.imgy)
                win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)                
                win32gui.SendMessage(hwnd, win32con.WM_CLOSE,0,0)
                self._userID += 1
                self._userID_changed = True
                return True 

            if self.SearchImage(hwnd,'colab_play_ground') == True:                
                if self.make_new_colab_page(hwnd) == True:
                        print('原来的帐号未收藏，增加收藏成功！')

                # 关闭浏览器
                win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)                
                win32gui.SendMessage(hwnd, win32con.WM_CLOSE,0,0)
                self._userID += 1
                self._userID_changed = True
                return True   

            if self.SQL.GetOneUnunsedEmail() == False:
                print('数据库中已没有未使用用户了！')
                return False   

            self.close_all_page(hwnd)  # 关闭所有的页面
            self.ImgLeftClickByHwnd(hwnd,'favorite_colab')    # 点击收藏夹                

            # 等待输入 email
            if self.input_email_address(hwnd) == False:
                continue
            # 输入口令
            if self.input_email_password(hwnd) == False:
                continue
     
            # 另存为副本再收藏一下
            if self.make_new_colab_page(hwnd) == False:
                continue
            else:     
                self._userID += 1
                self.cfg = yaml.safe_load(open(self._config_dir,'r').read())  
                self.cfg['userID'] = self._userID                
                self.save_yaml()

                self._userID_changed = True
                # 关闭浏览器
                if self.SearchImage(hwnd,'360js_close', _isCap=True) == True:
                    time.sleep(2.0) 
                    self.WinLeftClick(hwnd,self.imgx,self.imgy)
            
                print('添加一个用户成功了, 当前编号：' + str(self._userID))                
                self.SQL.SetEmailUsedAlready()
                return True        
        
        print('添加用户失败！')
        return False

    # 添加所有的用户
    def add_user(self):        
        
        #ok = 0
        while True:

            self.err_captrue = 0

            time.sleep(1.0)

            if self._userID_changed == True:  
                # 打开新窗口
                if self.openWebByUserID(self._userID) == False:
                    print('打开极速360程序失败！')
                    return False
                hwnd = self.getHwndByUserID(self._userID)  
                self._userID_changed = False
            
            if self.add_one_user(hwnd) == False:               
                break 
                 

    def make_new_colab_page(self,hwnd):

        # 再作一些处理

        INNEW = False

        t = 0
        while True:          

            print('正在新建笔记本副本 ... ID: ' + str(self._userID) + ' t=' + str(t))
            t += 1
            if t > self.cfg['inputGmailTryTimes']:
                return False

            # 弹出对话框
            if INNEW == False:
                # 菜单处理
                if self.SearchImage(hwnd,'colab_playground',_isCap=True) == True:
                    if self.ImgLeftClickByHwnd(hwnd,'colab_playground_file') == True:
                        time.sleep(0.2)
                        if self.ImgLeftClickByHwnd(hwnd,'colab_save_copy_cloud',_isCap=True)==True:
                            print('在云盘中另存一个副本')
                            INNEW = True

            if self.SearchImage(hwnd,'colab_copy_is_finished') == True:
                if self.ImgLeftClickByHwnd(hwnd,'colab_open_in_newpage') == True:
                    print('在新标签中打开副本')
                elif self.ImgLeftClickByHwnd(hwnd,'colab_open_in_newpage_2') == True:
                    print('在新标签中打开副本')

            # make_new_colab_page_again err_cannot_copy_juypter
            if self.SearchImage(hwnd,'err_cannot_find_juypter') == True: 
                return False

            if self.SearchImage(hwnd,'err_cannot_copy_juypter') == True: 
                return False


            if self.SearchImage(hwnd,'now_lookuping_and_down') == True:
                if self.ImgLeftClickByHwnd(hwnd,'colab_down_arrow') == True:
                    print('放下菜单项目')
                
            
            if self.ImgLeftClickByHwnd(hwnd,'very_satisfied',_isCap=False) == True:
                time.sleep(1.0) #skip_question
                if self.ImgLeftClickByHwnd(hwnd,'skip_question') == True:
                    print('skip_question')

            if self.SearchImage(hwnd,'colab_quota_exceeded') == True:
                if self.ImgLeftClickByHwnd(hwnd,'colab_quota_exceeded_ok') == True:
                    print('colab_quota_exceeded_ok')
                elif self.ImgLeftClickByHwnd(hwnd,'colab_quota_exceeded_ok2') == True:
                    print('colab_quota_exceeded_ok')

            if self.SearchImage(hwnd,'colab_quota_new_note') == True:
                if self.ImgLeftClickByHwnd(hwnd,'colab_quota_new_note_copy') == True:
                    print('colab_quota_new_note_copy')

            
            if self.SearchImage(hwnd,'colab_new_copy_finished') == True:
                print('副本加载成功了') 
                # 再收藏一下
                if self.colab_add_to_favorite_again(hwnd) == True:
                    return True
                

            if self.SearchImage(hwnd,'cannt_find_notebook',_isCap=True) == True:
                print('不能发现笔记本！')
                pass


    def colab_add_to_favorite_again(self,hwnd):

        
       
        CLICK_5 = False
        # 查找是不是已加入了:
        t = 0
        while True:
            print('收藏colab again...ID: ' + str(self._userID) + ' t:' + str(t) )
            t += 1

            if self.SearchImage(hwnd,'colab_favorite_2piece',_isCap=True) == True:
                print('已加入收藏夹了 again')
                return True   

            # 如果没有点开，就要点开一下 
            if self.SearchImage(hwnd,'colab_down_arrow') == True:
                if self.ImgLeftClickByHwnd(hwnd,'colab_down_arrow') == True:
                    print('放下菜单项目') 

            if CLICK_5 == False:
                if self.SearchImage(hwnd,'colab_play_copyed') == True:
                    # 点击收藏夹
                    if self.ImgLeftClickByHwnd(hwnd,'js360_favorite_icon') == True:
                        print('点击收藏五角星')
                        CLICK_5 = True

            #if self.ImgLeftClickByHwnd(hwnd,'js360_favorite_yes', '360js_favorite_ok', _isCap=False) == True:
            #    print('点击收藏 确认')
            if self.SearchImage(hwnd,'colab_quota_exceeded') == True:
                if self.ImgLeftClickByHwnd(hwnd,'colab_quota_exceeded_ok') == True:
                    print('colab_quota_exceeded_ok')
                elif self.ImgLeftClickByHwnd(hwnd,'colab_quota_exceeded_ok2') == True:
                    print('colab_quota_exceeded_ok')

            if self.SearchImage(hwnd,'colab_quota_new_note') == True:
                if self.ImgLeftClickByHwnd(hwnd,'colab_quota_new_note_copy') == True:
                    print('colab_quota_new_note_copy')

            # 查找跳出的窗口
            hwndList = self.get_child_windows(0)
            for hwndgg in hwndList:
                try:
                    className = win32gui.GetClassName(hwndgg)            
                    if className == 'Chrome_WidgetWin_2':

                        # 得到窗口大小 
                        _, top, _, bottom = win32gui.GetWindowRect(hwndgg)
                        h = bottom - top
                        if h == 451:
                            print('find windows: ', hex(hwndgg))

                            win32api.PostMessage(hwndgg, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                            win32api.SendMessage(hwndgg, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                            break

                            # 点击添加
                            #if self.ImgLeftClickByHwnd(hwndgg,'js360_favorite_yes', '360js_favorite_ok', _isCap=False) == True:
                            #    print('点击收藏 确认 x: ' + str(self.imgx) + ' y: ' + str(self.imgy))
                            #    time.sleep(1.0)                                                                    

                except:
                    pass

    
    def send_input_hax(self,_hwnd,_msg):

        def char2key(c):
            result = windll.User32.VkKeyScanW(ord(c))
            shift_state = (result & 0xFF00) >> 8
            vk_key = result & 0xff
            return shift_state, vk_key
        
        hwnd = _hwnd
        #win32gui.SendMessage(hwnd, win32con.WM_ACTIVATE,win32con.WA_ACTIVE,0)
        for c in _msg:            
            if c == "\n":
                win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            else:
                shift_state, vk_key = char2key(c)

                if shift_state == 1:
                    win32api.keybd_event(0xa1, 0,0,0)
                    time.sleep(0.05)
                    win32api.PostMessage(_hwnd, win32con.WM_KEYDOWN, vk_key, 0)
                    win32api.keybd_event(0xa1,0 ,win32con.KEYEVENTF_KEYUP ,0)
                else:
                    win32api.PostMessage(_hwnd, win32con.WM_KEYDOWN, vk_key, 0)       
                 
            time.sleep(0.05)   

    def openWebByUserID(self, _userID):

        '''
        hwndOld = []
        hwndList = self.get_child_windows(0)
        for hwnd in hwndList:
            try:
                className = win32gui.GetClassName(hwnd)  
                #print(className)          
                if className == 'Chrome_WidgetWin_1':
                   hwndOld.append(hwnd)

            except:                
                pass
        '''
        if self._get_360_new_hwnd(_userID) == True:
            return True
        
        cmd = self._webExePath + ' "--user-data-dir=' + self._userPath + '/GGcolab' + str(_userID) + '"'
        
        try:
           #hp, ht, pid, tid = win32process.CreateProcess(None, cmd,
            win32process.CreateProcess(None, cmd,
                                 # no special security
                                 None, None,
                                 # must inherit handles to pass std
                                 # handles
                                 0,
                                 0,
                                 None,
                                 None,
                                 win32process.STARTUPINFO())
        except Exception as e:
            # Translate pywintypes.error to WindowsError, which is
            # a subclass of OSError.  FIXME: We should really
            # translate errno using _sys_errlist (or simliar), but
            # how can this be done from Python?
            raise WindowsError(*e.args)     
        t = 0
        while True:
            print('正在等待360新窗口')
            time.sleep(1.0)
            if self._get_360_new_hwnd(_userID) == True:   
                hwnd = self.getHwndByUserID(_userID)
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                w = right - left
                if w != 900:
                    w = 900
                h = bottom - top
                if h != 800:
                    h = 800
                win32gui.MoveWindow(hwnd,left,top,w,h,True)
                return True
            t += 1
            if t > 30:
                self.openWebByUserID(_userID)

    def _get_360_new_hwnd(self, _userID):
        hwndList = self.get_child_windows(0)
        for hwnd in hwndList:
            try:
                className = win32gui.GetClassName(hwnd)            
                if className == 'Chrome_WidgetWin_1':
                    title = win32gui.GetWindowText(hwnd)
                    sub1 = '360'  
                    sub2 = '欢迎使用360'
                    sub3 = '您访问'                                   
                    if title.find(sub1) == 0 or title.find(sub2) == 0 or title.find(sub3) == 0:
                        win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)    
                        self.Hwnds360[_userID] = hwnd
                        print('已成功打开窗口： ', hex(hwnd))          
                        return True
            except:
                pass
        return False

    def _get_360_new_hwnd_2(self, _hwndOLD):
        hwndList = self.get_child_windows(0)
        for hwnd in hwndList:
            try:
                className = win32gui.GetClassName(hwnd)            
                if className == 'Chrome_WidgetWin_1':

                    title = win32gui.GetWindowText(hwnd)

                    sub = self.cfg['newPageTile']

                    if title.find(sub) != -1:
                        self.save_yaml()
                        return hwnd

                    # 得到窗口大小 
                    _, top, _, bottom = win32gui.GetWindowRect(hwnd)
                    h = bottom - top
                    if h < 200:
                        # print('hwnd to short:', hex(hwnd))
                        continue

                    findalready = False
                    for oldhwnd in _hwndOLD:
                        if oldhwnd == hwnd:
                            findalready = True
                            break
                    if findalready == False:                        
                        return hwnd

            except:
                pass

        return -1

    def _get_hwndsbyPid(self, pid):
        """return a list of window handlers based on it process id"""
        def callback(hwnd, hwnds):
            #if win32gui.IsWindowVisible(hwnd): # and win32gui.IsWindowEnabled(hwnd):
            #    if win32gui.GetParent(hwnd) == None:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
            return True
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return hwnds 
    
    def ImgLeftClickByHwnd(self, _hwnd, _Tname, _Mname='tmp', _isCap=True, _xoff = 0, _yoff=0):

        if _isCap == True:
            self.CaptureOne(_Mname,_hwnd)

        if self.SearchImage(_hwnd, _Tname,_Mname) == True:
            # client_pos = [self.imgx, self.imgy]
            self.WinLeftClick(_hwnd, self.imgx+_xoff, self.imgy+_yoff)
            return True
        return False

    def WinLeftClick(self, _hwnd, _x, _y):
        client_pos = [_x, _y]
        tmp=win32api.MAKELONG(client_pos[0],client_pos[1])
        win32gui.SendMessage(_hwnd, win32con.WM_ACTIVATE,win32con.WA_ACTIVE,0)
        win32gui.SendMessage(_hwnd, win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,tmp)    
        win32gui.SendMessage(_hwnd, win32con.WM_LBUTTONUP,0,tmp)

    # 查找一个图，返回位置
    def SearchImage(self, _hwnd, _timgFileName, _mainImgFileName='tmp', _isCap = False, _threshold = 0.90):

        if _isCap == True:
            self.CaptureOne(_mainImgFileName, _hwnd)

        _timgFileName = _timgFileName + self.PIC_SELECT_FORMAT
        _mainImgFileName = _mainImgFileName + self.PIC_CAP_FORMAT

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

        if _threshold == 0.99:
            pass
        else:
            threshold = self.cfg['findPrecision']

        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):
            self.imgx = int(pt[0] + template_size[1] / 2)
            self.imgy = int(pt[1] + template_size[0] / 2)
            if self.imgx > 10 and self.imgy > 10:
                return True
        return False

    def CaptureOne(self, _filename, _hwnd):    
        try:
            self.CaptureOneNotry(_filename, _hwnd)
            self.err_captrue = 0
        except:
            print('截图出错！', _filename, 'hwnd:', hex(_hwnd))
            self.err_captrue += 1
    
    def CaptureOneNotryRect(self, _filename, _hwnd, left,top,right,bottom):
        time.sleep(0.5)        

        _filename = _filename + '.png'               

        # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）  
        hwndDC = win32gui.GetWindowDC(_hwnd)
        # 根据窗口的DC获取mfcDC
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        # mfcDC创建可兼容的DC
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建bigmap准备保存图片
        saveBitMap = win32ui.CreateBitmap()

        # 获取窗口大小
        #left, top, right, bottom = win32gui.GetWindowRect(_hwnd)
        w = right - left
        h = bottom - top

        # 为bitmap开辟空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        # 高度saveDC，将截图保存到saveBitmap中
        saveDC.SelectObject(saveBitMap)
        # 截取从左上角（0，0）长宽为（w，h）的图片
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (left, top), win32con.SRCCOPY)

        saveBitMap.SaveBitmapFile(saveDC, self.getFindPath() + _filename)   

        # Free Resources
        mfcDC.DeleteDC()
        saveDC.DeleteDC()
        win32gui.ReleaseDC(_hwnd, hwndDC)
        win32gui.DeleteObject(saveBitMap.GetHandle())   

    # 抓图一个
    def CaptureOneNotry(self, _filename, _hwnd):
        # _hwnd=0 为桌面窗口  

        time.sleep(0.5)

        _filename = _filename + self.PIC_CAP_FORMAT                  

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

         # Free Resources
        mfcDC.DeleteDC()
        saveDC.DeleteDC()
        win32gui.ReleaseDC(_hwnd, hwndDC)
        win32gui.DeleteObject(saveBitMap.GetHandle())   


    def getPicPath(self):
        return './resource/image/'

    def getFindPath(self):
        return './resource/imagefind/'

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

     
