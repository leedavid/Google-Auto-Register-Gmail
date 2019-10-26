#!/usr/bin/env python3

import sys
import os
import time
import random
import string
import sqlite3
# import logging
from common.sms51ym import SMS51ym

# Function used to randomize credentials
def randomize(_option_, _length_):

    if _length_ > 0 :

        # Options:
        #       -p      for letters, numbers and symbols
        #       -l      for letters only
        #       -n      for numbers only
        #       -m      for month selection
        #       -d      for day selection
        #       -y      for year selection

        if _option_ == '-p':
            #string._characters_='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!#$*()_+'
            string._characters_='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        elif _option_ == '-l':
            #string._characters_='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            string._characters_='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        elif _option_ == '-n':
            string._characters_='1234567890'
        elif _option_ == '-m':
            string._characters_='JFMASOND'

        if _option_ == '-d':
            _generated_info_=random.randint(1,28)
        elif _option_ == '-y':
            _generated_info_=random.randint(1960,2002)
        else:
            _generated_info_=''
            for _ in range(0,_length_) :
                _generated_info_= _generated_info_ + random.choice(string._characters_)

        return _generated_info_

    else:
       print('No valid length specified...')
       exit(0)


class Gmail:

    def __init__(self):
        self._id = -1
        self._first_name = randomize('-l', random.randint(6,12))
        self._last_name = randomize('-l', random.randint(4,10))
        self._email = randomize('-l',random.randint(3,8)) + str(randomize('-y',1)) + randomize('-l',random.randint(2,5))
        self._password = randomize('-p',random.randint(8,14))
        self._phone = '-1'
        self._base_email = randomize('-l',8) + '@' + '163' + '.com'
        self._year = randomize('-y',1)
        self._month = randomize('-m',1)
        self._date = randomize('-d',1)
        self._from = 'a' 
        self._note = 'n'
        self._inputdate = time.gmtime()

        #LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        #logging.basicConfig(filename='my.log', level=logging.DEBUG, format=LOG_FORMAT)


    def _insertErrorMail(self,_conn):

        lpass = self._password
        email = self._email

        sql = ('insert into tgError ('
        'email,'
        'password,'
        'exmail'
        ') '
        'values ('
        "'%s'," % email +
        "'%s'," % lpass +
        "'%s')" % self._base_email)

        cursor = _conn.cursor()                       
        cursor.execute(sql)
        cursor.close()
        _conn.commit()

    def insertToDB(self, _conn):

        lpass = self._password  #.lower()  # TO DO 

        email = self._email   # .lower()
        pos = self._email.find('@')
        if pos == -1:
            email = email + '@gmail.com'

        sql = ('insert into tgmail ('
            'first_name,'
            'last_name,'
            'email,'
            'password,'
            'phone,'
            'base_email,'
            'year,'
            'month,'
            'dates,'
            'fromwhere,'
            'note,'
            'isUse'
            ')'
            'values ('
            "'%s'," % self._first_name + 
            "'%s'," % self._last_name +
            "'%s'," % email + 
            "'%s'," % lpass +                 #####
            "'%s'," % self._phone + 
            "'%s'," % self._base_email + 
            "'%s'," % str(self._year) + 
            "'%s'," % self._month + 
            "'%s'," % str(self._date) + 
            "'%s'," % self._from + 
            "'%s'," % self._note + 
            "'%s')" % 'N')

        cursor = _conn.cursor()                       
        cursor.execute(sql)
        cursor.close()
        _conn.commit()
        #self._conn.close()

    def _GetOneUnunsedEmail(self,_conn):       

        sql = 'SELECT id, email, password, phone, base_email from tgmail WHERE isUse = "N"'

        cursor = _conn.cursor()    
        cursor = _conn.execute(sql)

        for row in cursor:
            self._id = row[0]
            self._email = row[1]
            self._password = row[2]
            self._phone = row[3]
            self._base_email = row[4]

            cursor.close()

            pos = self._email.find('@')

            if pos == -1:
                self._email = self._email + '@gmail.com'

            return True

        return False

    def _SetEmailUsedAlready(self,_conn):

        sql = ('UPDATE tgmail set isUse = "Y", note = "%s" where id = "%d"' %(self._note, self._id))

        cursor = _conn.cursor()    
        cursor = _conn.execute(sql)
        _conn.commit()
        cursor.close()

    

    def _DeleteEmailByBan(self,_conn):

        self._insertErrorMail(_conn)   # 将删除的邮箱保存一下

        sql = ('DELETE from tgmail where id = "%d"' % self._id)        

        cursor = _conn.cursor()    
        cursor = _conn.execute(sql)
        _conn.commit()
        cursor.close()

class CGmailSqlite:

    def __init__(self,dbName):
      
        self._conn = sqlite3.connect(dbName)   
        self._gmail = Gmail()

        self._success = True
        self._err = '正常'
        self._tryNUm = 0

        # 登录 sms sever
        self._sms = SMS51ym()
        if self._sms.Gettoken() == False: 
            print("不能登录网络")       
            return

    def __del__(self):
        self._conn.close()

    def InitEmail(self):
        self._gmail = Gmail()
        self._success = True
        #self._tryNUm = 3           # 只试三次，就不来了

    def GetOneUnunsedEmail(self):       # 得到一个没有使用过的email
        return self._gmail._GetOneUnunsedEmail(self._conn) 

    def SetEmailUsedAlready(self):
        return self._gmail._SetEmailUsedAlready(self._conn)

    def DeleteEmailByBan(self):
        return self._gmail._DeleteEmailByBan(self._conn)

    def createTable(self):
        

        sql = ("CREATE TABLE tgmail ( `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, "
        "`first_name` VARCHAR ( 20 ) NOT NULL DEFAULT 'lee', `last_name` VARCHAR ( 20 ) " 
        " NOT NULL DEFAULT 'david', `email` VARCHAR ( 50 ) NOT NULL, `password` VARCHAR "
        "( 20 ) NOT NULL, `phone` VARCHAR ( 20 ) DEFAULT -1, `base_email` VARCHAR ( 50 ) "
        "DEFAULT 'N', `year` VARCHAR ( 10 ) DEFAULT 2018, `month` VARCHAR ( 10 ) DEFAULT 12,"
        " `dates` VARCHAR ( 10 ) DEFAULT 21, `fromwhere` VARCHAR ( 20 ) DEFAULT 'tb', `note` "
        "VARCHAR ( 50 ) DEFAULT 'note', `inputdate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, `isUse` CHAR ( 10 ) DEFAULT 'N' ))")     

        cursor = self._conn.cursor()    
        cursor = self._conn.execute(sql)
        self._conn.commit()
        cursor.close()

    def getPhoneNumber(self):
        self._sms.GetPhoneNumber()
        self._gmail._phone = self._sms._phone  

    def getSms(self):    
        self._sms.GetSmSbyPhone(90.0)

    def insertOneGmail(self):
        self._gmail.insertToDB(self._conn)

    def GetPointPhoneNumber(self):
        if len(self._gmail._phone) > 8:
            self._sms._phone = self._gmail._phone
        return self._sms.GetPointPhoneNumber()



    def AddIngorePhone(self):
        self._sms.ReleasePhoneNumber()
        self._sms.AddIgnoreNumber()

       
