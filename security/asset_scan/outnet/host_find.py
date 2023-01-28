# -*- coding: utf-8 -*-
import sys
import time
import re
import subprocess
from IPy import IP
import MySQLdb
import MySQLdb as mysql

CDATES= time.strftime('%Y-%m-%d', time.localtime(time.time()))
CTIMES = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
NMSCAN = 'nmap -n -sP -iL {0} -oN {1}'
ALLIP = ""
ip_file = "/home//outipscan/all_port_scan_ip_list.txt"
# ip_file = "nmap_in.txt"
nmap_out_file = "/home//outipscan/idc_ip_nmap_out.txt"
# nmap_out_file = "nmap_out.txt"


class mydb():
    def __init__(self):
        self.name = 'mydb'
        self.conn = None

    def connect(self):
        # self.conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='avds', charset='utf8')
        self.conn = MySQLdb.connect(host='569', user='apps', passwd='i100ps', db='avds', charset='utf8')
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
    print 'job start'
    global ALLIP
    conn = mydb()
    curs = conn.cursor()
    curs.execute("SELECT publicIpAddress from cms_hosts WHERE host_position = 'idc' and networkType='outer'")
    idc_ip = curs.fetchall()
    for ip in idc_ip:
        ALLIP += ip[0] + '\n'
    with open(ip_file,'w') as f:
        f.write(ALLIP)
    stdt, _ = run_command(NMSCAN.format(ip_file,nmap_out_file))
    print NMSCAN.format(ip_file,nmap_out_file)
    with open(nmap_out_file,'r') as r:
        for host in r.readlines():
            ip = re.findall('\d+\.\d+\.\d+\.\d+', host)
            if ip:
                #print ip[0]
                sql = '''update idc_outerip set type=1,update_time=%s where ip=%s'''
                curs.execute(sql, (CTIMES, ip[0]))
                curs.execute("update cms_hosts set `status`='Running',updateTime='%s' where publicIpAddress= '%s'" % (CDATES,ip[0]))
                print "update cms_hosts set `status`='Running',updateTime='%s' where publicIpAddress= '%s'" % (CTIMES,ip[0])
    curs.close()
    conn.close()

def run_command(cmd):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sp.wait()
    return sp.communicate()

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    conn = mydb()
    curs = conn.cursor()
    curs.execute("update cms_hosts set `status`='Stopped' where host_position = 'idc' and networkType='outer'")
    get_iplist()
    print 'job success'
    curs.close()
    conn.close()
