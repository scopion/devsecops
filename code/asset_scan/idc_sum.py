# -*- coding: utf-8 -*-
#!/usr/bin/env python
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

CTIMES = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
class mydb():
    def __init__(self):
        self.name = 'mydb'
        self.conn = None

    def connect(self):
        self.conn = MySQLdb.connect(host='569', user='apps', passwd='i10ps', db='avds', charset='utf8')
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

def idcsum(reg):
    conn = mydb()
    curs = conn.cursor()
    curs.execute("SELECT COUNT(*) FROM cms_hosts where host_position = 'idc' and networkType='inner' and regionId = '%s'" % (reg,))
    all_in_num = curs.fetchall()[0][0]
    curs.execute("SELECT COUNT(*) FROM cms_hosts where host_position = 'idc' and `status` = 'Running' and networkType='inner' and regionId = '%s'" % (reg,))
    if reg == '中经云机房':
        active_in = '318'
    else:
        active_in = curs.fetchall()[0][0]
    curs.execute("SELECT COUNT(*) FROM cms_hosts where host_position = 'idc' and networkType='outer' and regionId = '%s'" % (reg,))
    all_out_sum = curs.fetchall()[0][0]
    curs.execute(
        "SELECT COUNT(*) FROM cms_hosts where host_position = 'idc' and `status` = 'Running' and networkType='outer' and regionId = '%s'" % (
        reg,))
    active_out= curs.fetchall()[0][0]
    print reg,all_in_num,active_in,all_out_sum,active_out
    curs.execute("update cms_idc set ipsum = %s,activesum= %s,outeractivesum=%s,outeripsum=%s,updatetime='%s' where location like '%s'" % (all_in_num, active_in,active_out,all_out_sum, CTIMES, reg))
    curs.close()
    conn.close()



if __name__=="__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    conn = mydb()
    curs = conn.cursor()
    curs.execute("select location from cms_idc")
    idclist = curs.fetchall()
    for idc in idclist:
        print idc[0]
        idcsum(idc[0])


