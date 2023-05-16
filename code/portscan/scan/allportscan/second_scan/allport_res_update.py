# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
import nmap

CDATES = time.strftime('%Y-%m-%d', time.localtime(time.time()))
SHAREM = Queue.Queue()

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

def run_command(cmd):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.wait()
    return sp.communicate()


def read_data():
    conn = mydb()
    curs = conn.cursor()
    sql = '''select ip,port from all_port where `status`=1 and cdate like %s'''
    curs.execute(sql,(CDATES,))
    results = curs.fetchall()
    for result in results:
        ip = result[0]
        port = result[-1]
        ints = '%s#%s' % (ip,port)
        SHAREM.put(ints)
    curs.close()
    conn.close()

def second_scan():
    conn = mydb()
    curs = conn.cursor()
    nm = nmap.PortScanner()
    while not SHAREM.empty():
        try:
            recd = SHAREM.get(False)
        except Queue.Empty:
            break
        ippt = recd.split("#")
        print("Nmap scan %s:%s start...\n" %(ippt[0], ippt[1]))
        # stdt, _= run_command(SVSCAN.format(ippt[0], ippt[1]))
        nm.scan(hosts=ippt[0], arguments='-n -sV -Pn -p'+ippt[1])
        status = nm[ippt[0]]['tcp'][int(ippt[1])]['state']
        if 'open' in status:
            print status,ippt
        else:
            print status,ippt
            curs.execute("update all_port set `status` = 0 where ip = '%s' and port = '%s'" % (ippt[0], ippt[1]))
        SHAREM.task_done()
    curs.execute("update all_port set `status` =1 WHERE banner REGEXP 'WebLogic'")
    curs.close()
    conn.close()


def white_list():
    with open('/home/workspace/source/ip_port_white.txt','r') as f:
        lists = f.readlines()
        conn = mydb()
        curs = conn.cursor()
        for ip_port in lists:
            ipport = ip_port.split(':')
            ip =ipport[0]
            port = ipport[-1]
            sql = "DELETE FROM all_port WHERE ip = %s and `port` = %s"
            curs.execute(sql,(ip,port))
            result = curs.rowcount
            print sql % (ip,port)
            print 'white'+ip+':'+port+'del success',result
    curs.close()
    conn.close()




class MyThread(threading.Thread):
    def __init__(self, func):
        super(MyThread, self).__init__()
        self.func = func

    def run(self):
        self.func()

if __name__=="__main__":
    conn = mydb()
    curs = conn.cursor()
    # curs.execute("UPDATE all_port,port_service SET all_port.`status` =1 WHERE all_port.cdate LIKE '%s' AND all_port.service = port_service.service" % (CDATES,))
    reload(sys)
    sys.setdefaultencoding('utf-8')
    read_data()
    # second_scan()
    threads = []
    for i in xrange(10):
        thread = MyThread(second_scan)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    SHAREM.join()
    white_list()
    conn.close()
