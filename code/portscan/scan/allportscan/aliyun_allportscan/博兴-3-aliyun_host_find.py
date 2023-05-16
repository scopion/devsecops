# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
import os
import sys
import time
import json
import redis
import Queue
import socket
import smtplib
import MySQLdb
import datetime
import requests
import threading
import subprocess
from ding_msg import *


CDATES = time.strftime('%Y-%m-%d', time.localtime(time.time()))
CTIMES = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
SCANFP = "/home//allportscan/all_port_scan_ip_list.txt"
ALLIPS = ''


class mydb():
    def __init__(self):
        self.name = 'mydb'
        self.conn = None

    def connect(self):
#        self.conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='avds',charset='utf8')
        self.conn.autocommit(True)

    def cursor(self):
        try:
            self.conn.ping()
            curs = self.conn.cursor()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            curs = self.conn.cursor()
        return curs

    def close(self):
        if self.conn:
            self.conn.close()


def get_iplist():
    i =0
    print '开始获取扫描ip'
    global ALLIPS
    conn = mydb()
    curs = conn.cursor()
    # curs.execute("update oms_portscan set before_times=times")
    # print '发现次数同步'
    curs.execute("select count(*) FROM cloudhost WHERE DATE_FORMAT(updateTime,'%Y-%m-%d') = DATE_FORMAT(NOW(), '%Y-%m-%d');")
    now_num = curs.fetchall()[0][0]
    print 'success is',now_num
    curs.execute("select count(*) FROM cloudhost WHERE DATE_FORMAT(updateTime,'%Y-%m-%d') != DATE_FORMAT(NOW(), '%Y-%m-%d');")
    num = curs.fetchall()[0][0]
    print 'faile is',num
    try:
        curs.execute("select publicIpAddress,eipAddress from cloudhost where updateTime like '%s'" % ('%'+CDATES+'%',))
    except Exception,e:
        print e
    all_result = curs.fetchall()
    ip_num = len(all_result)/5
    print 'all ip num is',len(all_result)
    for item in all_result[ip_num*2+1:]:
#        print item
        if item[0]:
            ALLIPS += item[0] + "\n"
        elif item[-1]:
            ALLIPS += item[-1] + "\n"
        else:
            pass
        i = i +1
        if  i == len(all_result)/5:
             break
    curs.close()
    conn.close()
    print '开始写入文件'
    with open(SCANFP, 'w') as fl:
        fl.write(ALLIPS)
    #计算文件行数
    count = 0
    for index, line in enumerate(open(SCANFP, 'r')):
        count += 1
    print count

def run_command(cmd):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.wait()
    return sp.communicate()

def deleteOutdateFiles(path):
    current_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    current_timeList = current_time.split("-")
    current_time_day = datetime.datetime(int(current_timeList[0]), int(current_timeList[1]), int(current_timeList[2]))
#root是当前路径，dirs路径下所有子目录，files是当前路径下所有非目录子文件
    for root, dirs, files in os.walk(path):
        for item in files:
            name = os.path.splitext(item)[0]
            file_path = os.path.join(root, item)
            ret = re.findall("all_port_scan_jresult_know",name)
            create_time = time.strftime("%Y-%m-%d", time.localtime((os.stat(file_path)).st_mtime))
            create_timeList = create_time.split("-")
            create_time_day = datetime.datetime(int(create_timeList[0]), int(create_timeList[1]),
                                                int(create_timeList[2]))
            time_difference = (current_time_day - create_time_day).days
            if time_difference > 2 and ret:
                os.remove(file_path)


if __name__=="__main__":
    path = "/home//allportscan/"
    reload(sys)
    sys.setdefaultencoding('utf-8')
    get_iplist()
    deleteOutdateFiles(path)
