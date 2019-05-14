#! /usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'william'

import pymysql
import requests
import time
import configparser
import logging

# 设置LOG打印信息
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s - %(lineno)d行"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGDATA_FORMAT = "%Y-%m-%d"
LOGADDR = 'LOG/{}.log'.format(time.strftime(LOGDATA_FORMAT, time.localtime()))
logging.basicConfig(filename=LOGADDR,level = logging.INFO, format=LOG_FORMAT,datefmt=DATE_FORMAT)

#导入配置文件内容
try:
    cf = configparser.ConfigParser()
    cf.read('config.ini')
    logging.info('导入配置文件成功！')
except Exception as e:
    logging.error('导入配置文件错误，程序退出！错误信息：e'.format(e))
    raise ValueError

# 连接到数据库  服务器地址，账号，密码，数据库名称(全部配置在配置文件内)
try:
    DB = pymysql.connect(cf.get('db','db_addr'),cf.get('db','db_usr'),cf.get('db','db_pwd'),cf.get('db','db_name'))
    cursor = DB.cursor()
    logging.info('数据库连接成功！')
except Exception as e:
    logging.error('数据库连接错误，程序退出！！错误信息：{}'.format(e))
    raise ValueError('DataBase init faild!!!!')

#下载网页数据
def download(url):
    response = requests.get(url)
    logging.debug("准备格式化并输出URL内容，URL：{}".format(url))
    try:
        return eval(response.text)  #返回一个格式化结果
    except Exception as e:
        logging.error('URL格式化错误，URL:{} 错误信息：{}'.format(url,e))
        raise ValueError('Create URL request favid!!!') #格式化错误，返回一個ValueError

# 时间处理（将一个stricttime转化为一个时间戳）
def TimeTransform(timestring):
    try:
        return time.mktime(time.strptime(timestring, '%Y-%m-%d'))
    except:
        try:
            return time.mktime(time.strptime(timestring, '%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            logging.debug('给处的stricttime有问题，转化失败！！stricttime:{}错误信息;{}'.format(timestring,e))
            raise ValueError('TimeTransform faild!!!!')  # 抛出一个value错误

#进行数据库操作
class Db(object):
    global DB
    #初始化DB，初始化当前的操作表
    def __init__(self,TableName,string = 0):
        self.TableName = TableName
        self.string = string

    #返回当前数据库最新一条信息的时间戳
    def GetMaxTime(self):
        maxtime = cf.get('dborder','getmaxtime').format(self.TableName)
        cursor.execute(maxtime)
        return cursor.fetchall()[0][0]

    #插入数据到数据库操作(5/15/30/60日操作方式)
    def InsertDb(self,list):
        if self.string == 0:
            InsertData = cf.get('dborder','insetdata').format(self.TableName,list[0],int(list[1].split(".")[0]), int(list[2].split(".")[0]), int(list[3].split(".")[0]), int(list[4].split(".")[0]), int(list[5]))
            logging.info('>>>>>>>内容存储到数据库：{}；存储数据表：{}'.format(list,self.TableName))
            cursor.execute(InsertData)
            DB.commit()

n_list = {}  # 插入数据库条数记录

for k,v in cf.items('url'): # k 数据库表名   v 下载连接
    dt = download(v)
    db = Db(k)
    if db.GetMaxTime() == None:  #判断是否可取到数据库时间数据，如时间数据为空，则取默认值 = 0
        db_maxtime = 0
    else:
        db_maxtime = db.GetMaxTime()
    for i in dt:
        dt_time = TimeTransform(i[0])
        if  dt_time > db_maxtime:
            db.InsertDb(i)
            if k in n_list:
                n_list[k] = n_list[k] + 1
            else:
                n_list[k] = 1
        else:
            pass

if __name__ =='__main__':
    if n_list == {}:
        print('-----------\n 无新增内容\n-----------')
    else:
        print('---数据库插入记录---')
        for k,v in n_list.items():
            print('  {}: {}条'.format(k,v))
        print('------------------')

DB.close()