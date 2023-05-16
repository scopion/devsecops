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


'''
mysql> desc net_scan;
+----------+---------------------+------+-----+--------------+----------------+
| Field    | Type                | Null | Key | Default      | Extra          |
+----------+---------------------+------+-----+--------------+----------------+
| id       | bigint(10) unsigned | NO   | PRI | NULL         | auto_increment |
| ip       | varchar(64)         | NO   | MUL | NULL         |                |
| port     | int(6)              | YES  |     | NULL         |                |
| protocol | varchar(16)         | YES  |     | NULL         |                |
| service  | varchar(128)        | YES  |     | NULL         |                |
| banner   | varchar(128)        | YES  |     | NULL         |                |
| cdate    | datetime            | NO   |     | NULL         |                |
| status   | int(1)              | YES  |     | 0            |                |
| os       | varchar(64)         | YES  |     | Linux 2.6.32 |                |
+----------+---------------------+------+-----+--------------+----------------+
'''

CDATES = time.strftime('%Y-%m-%d', time.localtime(time.time()))
CTIMES = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
ALLIPS = ""
SCANFP = "/home//allportscan/all_port_scan_ip_list1.txt"
MSREST = "/home//allportscan/all_port_scan_jresult_know_%s.json" % (CDATES)
RDPOOL = redis.ConnectionPool(host='127.0.0.1', port=6379)
REDSOP = redis.StrictRedis(connection_pool=RDPOOL)
# MSSCAN = '/usr/bin/masscan -iL {0} -p1-65535 --wait 3 --max-rate 10000 -oJ {1}'
MSSCAN = '/home/renhongwei/masscan/bin/masscan -iL {0} -p1-65535 --wait 3 --max-rate 10000 -oJ {1}'
UDPLST = ['123', '135', '137', '138', '139', '161', '1900', '11211']
SHAREM = Queue.Queue()
SVSCAN = '/usr/bin/nmap -sV -Pn {0} -p{1}'
SHAREN = Queue.Queue()
DELBLINE = "/home/workspace/source/delete.txt"

class mydb():
    def __init__(self):
        self.name = 'mydb'
        self.conn = None

    def connect(self):
        # self.conn = MySQLdb.connect(host='192.168.78.136', user='root', passwd='root', db='avds',charset='utf8')
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


def run_command(cmd):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.wait()
    return sp.communicate()



'''
/usr/bin/masscan -iL {0} -p1-65535 --banners --wait 3 --max-rate 10000
/usr/bin/masscan -iL {0} --top-ports 1000 --wait 3 --max-rate 10000 -oJ {1}
Initiating SYN Stealth Scan
Scanning 64 hosts [65535 ports/host]
Discovered open port 80/tcp on 4243
Discovered open port 443/tcp on 42.62.9.16
'''
def port_scan():
    conn = mydb()
    curs = conn.cursor()
    print '开始读取扫描结果'
    with open(MSREST, 'r') as f:
        for line in f:
            # print "line=",line
            if line.startswith('{'):
#                print("%s\n" %(line[:-1]))
                try:
                    item = json.loads(str(line[:-1]))
                except Exception,e:
                    print e
                port = item["ports"][0]
                if '80' not in str(port["port"]) or '443' not in str(port["port"]):
                    ints = "%s#%s" %(item["ip"], port["port"])
                    print ints
                    SHAREM.put(ints)



'''
/usr/bin/nmap --version-all {0} -p{1}
/usr/bin/nmap -sV {0} -p{1}
PORT      STATE SERVICE      VERSION
53/tcp    open  domain       Microsoft DNS
389/tcp   open  ldap
Running (JUST GUESSING): Microsoft Windows Vista|2008|7|Phone (93%)
'''
def service_scan():
    while not SHAREM.empty():
        try:
            recd = SHAREM.get(False)
        except Queue.Empty:
            break
        ippt = recd.split("#")
        print("Nmap scan %s:%s start...\n" %(ippt[0], ippt[1]))
        stdt, _= run_command(SVSCAN.format(ippt[0], ippt[1]))
        print SVSCAN.format(ippt[0],ippt[1])
        for rows in stdt.split('\n'):
            if "open" in rows:
                print rows
                item = rows.strip().split()
                ipts = item[0].split('/')
                banr = ' '.join(item[3:]) if len(item) > 3 else 'unknown'
                try:
                    inps = "%s=%s=%s=%s=%s=Linux 2.6.32" %(ippt[0], ipts[0], ipts[1], item[2].strip('?'), banr)
                except Exception,e:
                    print e
                SHAREN.put(inps)
                print("\tnew find service: %s\n" %(inps))
            else:
                print 'no new service'
        SHAREM.task_done()

'''
1.1.1.1=53=udp=domain=Microsoft DNS=Linux
'''
def record_save():
    bline = '无'
    phone = '无'
    group_id = '无'
    account = '无'
    conn = mydb()
    curs = conn.cursor()
    while not SHAREN.empty():
        try:
            item = SHAREN.get(False).split('=')
        except Queue.Empty:
            break
        print item
        curs.execute("SELECT instanceId,instanceName,opsuserid,busid,arn,regionId,host_position from cms_hosts where publicIpAddress ='%s' or eipAddress='%s'" % (item[0], item[0]))
        result = curs.fetchall()
        if result:
            instanceid = result[0][0]
            instancename = result[0][1]
            userid = result[0][2]
            group_id = result[0][3]
            arn = result[0][4]
            host_pos = result[0][6]
            regoid =str(host_pos)+'-'+result[0][5]
            curs.execute("select telephone from authorization_user where id = %s",(userid,))
            phone = curs.fetchall()[0][0]
            curs.execute("select account from authorization_arners where arn =%s",(arn,))
            account = curs.fetchall()[0][0]
            curs.execute("select refer from authorization_group where id = %s",(group_id,))
            bline = curs.fetchall()[0][0]
            print 'aliyun的机器', bline, item[0], account, instancename, regoid,phone
            sqls = '''INSERT IGNORE INTO all_port (ip, `port`, protocol, service, banner, cdate, group_id, bline, account, instancename, regoid, phone) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE cdate=%s'''
            curs.execute(sqls, (item[0], item[1], item[2], item[3], item[4], CDATES, group_id, bline, account, instancename, regoid, phone, CDATES))
            print (sqls % (item[0], item[1], item[2], item[3], item[4], CDATES, group_id, bline, account, instancename, regoid, phone, CDATES))
    print '新增端口记录'
#    f.write(DATA)
    curs.close()
    conn.close()

def white_list():
    with open('/home//allportscan/ip_port_white.txt','r') as f:
        lists = f.readlines()
        conn = mydb()
        curs = conn.cursor()
        for ip_port in lists:
            ipport = ip_port.split(':')
            ip =ipport[0]
            port = ipport[-1]
            sql = "DELETE FROM all_port WHERE ip = %s and `port` = %s"
            curs.execute(sql,(ip,port))

class MyThread(threading.Thread):
    def __init__(self, func):
        super(MyThread, self).__init__()
        self.func = func

    def run(self):
        self.func()


if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    port_scan()
    threads = []
    for i in xrange(10):
        thread = MyThread(service_scan)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    SHAREM.join()
    record_save()



