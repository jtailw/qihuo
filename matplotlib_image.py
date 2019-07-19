#! /usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'william'

import matplotlib.pyplot as plt
import pymysql
import configparser
import datetime
import time

try:
    cf = configparser.ConfigParser()    #读取配置文件，连接到数据库
    cf.read('config.ini')
    DB = pymysql.connect(cf.get('db','db_addr'),cf.get('db','db_usr'),cf.get('db','db_pwd'),cf.get('db','db_name'))
    cursor = DB.cursor()
except Exception as e:
    print(e)

class Db(object):
    # global DB

    def getdata(self,begintime,endtime):    #从数据库获取从开始时间到结束时间的数据
        data = str(cf.get('dborder','selecttime')).format(begintime,endtime)
        cursor.execute(data)
        return cursor.fetchall()

def timeinput():    #从键盘输入开始时间和结束时间
    def strtostrct_time(inputtime):    #将时间str字符串变换为strict_time
        try:
            return time.strptime(inputtime,'%Y-%m-%d')
        except Exception as e:
            print('ERROR:{}'.format(e))
            raise ImportError

    def strct_timetostr(inputtime):    #将strict_time变换为str字符串
        try:
            return time.strftime('%Y-%m-%d',inputtime)
        except Exception as e:
            print('ERROR:{}'.format(e))
            raise ImportError

    begintime = input('BEGINTIME(EX:1970-01-01):')  #从键盘获得开始时间输入
    if begintime != '':
        begintime = strtostrct_time(begintime)
        endtime = input('ENDTIME(EX:1970-01-01):')    #从键盘获得结束时间输入
        if endtime != '':
            endtime = strtostrct_time(endtime)
            if begintime >= endtime:    #判断开始时间和结束时间大小，开始时间必定小于结束时间
                begintime,endtime = endtime,begintime
            begintime = strct_timetostr(begintime)
            endtime = strct_timetostr(endtime)
            return begintime,endtime
        else:    #没有输入结束时间，则结束时间为开始时间向后延30天
            endtime1 = datetime.date(begintime.tm_year,begintime.tm_mon,begintime.tm_mday) + datetime.timedelta(days = 30)
            begintime = strct_timetostr(begintime)
            return begintime,endtime1
    else:    #没有输入开始时间，则默认从当前时间开始向前推30天
        begintime = datetime.datetime.today() - datetime.timedelta(days = 30)
        begintime = datetime.datetime.strftime(begintime,'%Y-%m-%d')
        endtime = datetime.datetime.today().strftime('%Y-%m-%d')
        return begintime,endtime

def DrawPlot():
    dd = Db()
    k,v =timeinput()
    c = dd.getdata(k,v)
    kk = []
    vv1 = []
    vv2 = []
    # vv3 = []

    for k,v1,v2,v3 in c:
        kk.append(k)
        vv1.append(v1)
        vv2.append(v2)
        # vv3.append(v3)

    for a,b in zip(kk,vv1):
        plt.text(a,b,b,ha = 'center',fontsize = 5)


    for a,b in zip(kk,vv2):
        plt.text(a,b,b,ha = 'center',fontsize = 5)

    plt.gcf().autofmt_xdate()
    plt.grid()
    plt.plot(kk,vv1)
    plt.plot(kk,vv2)
    plt.show()
    return


if __name__ == '__main__':
    DrawPlot()