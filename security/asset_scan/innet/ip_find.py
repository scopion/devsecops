# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import re
import sys
import time
import json
import redis
import Queue
import socket
import smtplib
import MySQLdb
import requests
import threading
import subprocess
import MySQLdb as mysql
from email.mime.text import MIMEText
import logging

CDATE = time.strftime('%Y-%m-%d', time.localtime(time.time()))
CDATES = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
iptxt = '/home//portscan/idc_cloud_pub_ip_know_'+CDATE+'.txt'
NMAPSCAN = 'nmap -n -sn -iL {0}'
nmap_outtxt = '/home//portscan/ip_list.txt'


class mydb():
    def __init__(self):
        self.name = 'mydb'
        self.conn = None

    def connect(self):
        self.conn = MySQLdb.connect(host='169', user='', passwd='i10ps', db='avds', charset='utf8')
        # self.conn = MySQLdb.connect(host='192.168.78.136', user='root', passwd='root', db='avds',charset='utf8')
        self.conn.autocommit(True)
        self.conn.ping(True)

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

def run_command(cmd):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.wait()
    return sp.communicate()


def get_iplist():
    conn = mydb()
    ALLIP = ''
    print '开始获取扫描ip'
    curs = conn.cursor()
    print iptxt
    f = open(nmap_outtxt,'r')
    # curs.execute("select ip from idc_outerip where bline = '集团' and `status`= 0 and address='机房'")
    #stdt, _ = run_command(NMAPSCAN.format(iptxt))
    for rows in f.readlines():
        host = re.findall('\d+\.\d+\.\d+\.\d+',rows)
        if host:
            ALLIP += host[0]+'\n'
            curs.execute("update idc_outerip set type =1 where ip = %s",(host[0],))
            curs.execute("update cms_hosts set `status`= 'Running',status_qingteng='Running',ip_updateflag=%s where privateIpAddress = %s",(CDATES,host[0]))
    with open(iptxt,'w') as l:
        l.write(ALLIP)
    curs.close()
    conn.close()
if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    get_iplist()
    print 'job end'
