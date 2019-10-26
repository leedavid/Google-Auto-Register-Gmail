#!/usr/bin/env python3


import requests
import sys
import time
import random
import string


class SMS51ym:

    def __init__(self):

        self._token = ''
        self._phone = ''
        self._smsMessage = ''
        self._smsOK = True

    def Gettoken(self):

        # http://api.fxhyd.cn/UserInterface.aspx?action=login&username=你的账号&password=你的密码
        # 登录成功：success|token
        # 登录失败：错误代码，请根据不同错误代码进行不同的处理

        url = 'http://api.fxhyd.cn/UserInterface.aspx?action=login&username=keersun&password=c2423346d9'
        r = requests.get(url)

        if r.status_code == 200:
            res = r.text.split('|')
            if res[0] == 'success':
                self._token = res[1]  
                print('log in 51ym sucess!')
                return True  
        print('log in 51ym Error!')
        return False
    
    def GetPhoneNumber(self):
        # 指定号码筛选规则，获取手机号码。
        # 必须	类型	字段名	名称	说明
        # √	字符串	action	接口类型	固定值：getmobile
        # √	字符串	token	令牌	登录接口获取的token值
        # √	整数	itemid	项目编号	项目对应的数字编号
        # ×	整数	isp	运营商代码	号码所属运营商代码。1:移动，2:联通，3:电信
        # ×	整数	province	省代码	号码归属地的省份代码，省市代码表。
        # ×	整数	city	市代码	号码归属地的市代码，省市代码表。
        # ×	整数	mobile	指定号码	要指定获取的号码，该号码必须是本平台的号码。
        # ×	字符串	excludeno	排除号段	不获取170、171和188号段的号码，则该参数为170.171.180，每个号段必须是前三位，用小数点分隔。
       
        # http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&token=TOKEN&itemid=项目编号&excludeno=排除号段
        # 获取成功：success|手机号码
        # 请求失败：错误代码，请根据不同错误代码进行不同的处理。暂停5秒再获取

        url = 'http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&token='+ self._token
        url = url + '&itemid=147&isp=1'
        r = requests.get(url)
        if r.status_code == 200:
            res = r.text.split('|')
            if res[0] == 'success':
                self._phone = res[1]  
                #nn = int(self._phone)
                #if(nn > 14000000000):
                #    print('get phonenumber too large! ', self._phone)
                #    self.GetPhoneNumber()
                print('get phonenumber ok: ', self._phone)
                return True  
        print('get phonenumber Error! ')
        return False

    def GetPointPhoneNumber(self):
        url = 'http://api.fxhyd.cn/UserInterface.aspx?action=getmobile&token='+ self._token
        url = url + '&itemid=147&mobile=' + self._phone
        r = requests.get(url)
        if r.status_code == 200:
            res = r.text.split('|')
            if res[0] == 'success':
                # self._phone = res[1]  
                print('get point phonenumber ok: ', self._phone)
                return True  
        print('get point phonenumber Error! ')
        return False


   

    def GetSmSbyPhone(self, delay):
        url = 'http://api.fxhyd.cn/UserInterface.aspx?action=getsms&token='+ self._token
        url = url + '&itemid=147&mobile=' + self._phone + '&release=1'

        if delay < 10:
            delay = 10

        Sdelay = delay

        while delay > 0:
            print('receive sms waiting: ', str(Sdelay-delay), ' s')
            time.sleep(1)
            delay = delay - 1 
            r = requests.get(url)
            if r.status_code == 200:
                res = r.text.split('|')
                if res[0] == 'success':
                    stotal = res[1]
                    smsList = stotal.split('-')  
                    self._smsMessage = smsList[1][0:6]
                    print('Get sms Phone: ', self._phone, " sms: ", self._smsMessage)
                    self._smsOK = True
                    return True
                elif res[0] == '2007':
                    self._smsOK = False
                    print('号码已被释放了！', res[0])
                    return False
                else:
                    print('res0: ', res[0], '短信尚未到达!!')                   
                    continue
            else:
                self._smsOK = False
                print('接收短信出错了！')
                return False
        print('Release PhoneNumber Error:', self._phone)
        self.AddIgnoreNumber()

        self._smsOK = False
        return False

    # 释放手机号码接口 
    # 释放指定的电话号码。如果号码不再使用请及时释放，否则你未释放的号码达到获取号码上限后将不能获取到新的号码。
    def ReleasePhoneNumber(self):
        url = 'http://api.fxhyd.cn/UserInterface.aspx?action=release&token='+ self._token
        url = url + '&itemid=147&mobile=' + self._phone + '&release=1'
        r = requests.get(url)
        if r.status_code == 200:
            res = r.text.split('|')
            if res[0] == 'success':                
                print('Release PhoneNumber Ok:', self._phone)
                return True
            else:
                print('Release PhoneNumber Error:', self._phone)
        return False
    
    def AddIgnoreNumber(self):
        url = 'http://api.fxhyd.cn/UserInterface.aspx?action=addignore&token='+ self._token
        url = url + '&itemid=147&mobile=' + self._phone
        r = requests.get(url)
        if r.status_code == 200:
            res = r.text.split('|')
            if res[0] == 'success':
                print('Ignore PhoneNumber Ok:', self._phone)
                return True
        print('Ignore PhoneNumber Error:', self._phone)
        return False
