import base64
import json
import logging
import time
import requests
from datetime import datetime, timedelta
import urllib.parse
import pymysql
import csv
import hmac
import hashlib
import base64
import urllib
import jsone

app_id = '136'
app_key = 'yNo0h'

session = requests.session()

def list_split(items, n):
    return [items[i:i+n] for i in range(0, len(items), n)]

def getmysqlconn():
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'avds',
        'passwd': 'i1ds',
        'db': 'avds',
        'charset': 'utf8',
        'cursorclass': pymysql.cursors.DictCursor
    }
    conn = pymysql.connect(**config)
    return conn

headers = {'Content-Type': 'application/json; charset=utf-8'}

def get(data,webhook):
    """
    发送消息（内容UTF-8编码）
    :param data: 消息数据（字典）
    :return: 返回发送结果
    """
    param = urllib.parse.urlencode(data)
    # response = self.session.post(hook, data=data).json()
    webhook = webhook + "?" + param
    #print (webhook)
    try:
        response = session.get(webhook)
    except requests.exceptions.HTTPError as exc:
        logging.error("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
        raise
    except requests.exceptions.ConnectionError:
        logging.error("消息发送失败，HTTP connection error!")
        raise
    except requests.exceptions.Timeout:
        logging.error("消息发送失败，Timeout error!")
        raise
    except requests.exceptions.RequestException:
        logging.error("消息发送失败, Request Exception!")
        raise
    else:
        try:
            result = response.json()
        except:
            logging.error("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
            return {'errcode': 500, 'errmsg': '服务器响应异常'}
        else:
            return result

def post(data,webhook):
    """
    发送消息（内容UTF-8编码）
    :param data: 消息数据（字典）
    :return: 返回发送结果
    """
    #data = json.dumps(data)
    try:
        #print (data)
        #print (webhook)
        response = session.post(webhook, data=data)
        #print (response.text)
    except requests.exceptions.HTTPError as exc:
        logging.error("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
        raise
    except requests.exceptions.ConnectionError:
        logging.error("消息发送失败，HTTP connection error!")
        raise
    except requests.exceptions.Timeout:
        logging.error("消息发送失败，Timeout error!")
        raise
    except requests.exceptions.RequestException:
        logging.error("消息发送失败, Request Exception!")
        raise
    else:
        try:
            result = response.json()
        except:
            logging.error("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
            return {'errcode': 500, 'errmsg': '服务器响应异常'}
        else:
            return result

#获取ticket
def getticket():
    data={"appid":app_id,"appkey":app_key}
    ticket_url = "http://a.com/basic/get_ticket"
    response = get(data,ticket_url)
    print (response)
    if response and response['errcode'] == 0:
        ticket = response['ticket']
    else:
        print ("获取ticket失败")
    return ticket

#获取员工信息
def get_empl_info(ticket,dept_ids=[],empl_classes=[],empl_ids=[],page=1,main=None):
    """
    markdown类型
    :param dept_ids: 部门ID
    :param empl_classes: 员工类型|分隔的员工类型列表，可为空，包括EFU（全职员工）、TFU（全职教师）、TAL（专职教师）、TPA（兼职教师）、EPA（兼职员工）、EPF（在编实习）、EPR（实习生）
    :param empl_ids: 员工ID
    :return: 返回消息发送结果
    """
    emplurl = "https://al.com/cmpts/data/main/empl/job/list"
    data = {
        "hr_status": "A",
    }
    data["ticket"] = ticket
    dept_id = '|'.join(set(dept_ids))
    data["dept_ids"] = dept_id
    empl_classe = '|'.join(set(empl_classes))
    data["empl_classes"] = empl_classe
    empl_id = '|'.join(set(empl_ids))
    data["empl_ids"] = empl_id
    data["page"] = page
    if main:
        data["main"] = main
    #print (data)
    logging.debug("获取员工信息：%s" % data)
    return get(data,emplurl)

#获取上级
def get_high(ticket,emplid):
    """
    markdown类型
    :param empl_ids: 员工ID
    :return: 返回消息发送结果
    """
    emplurl = "https://al.com/cmpts/data/main/higher/level"
    data = {}
    data["ticket"] = ticket
    data["emplid"] = emplid
    logging.debug("获取员工信息：%s" % data)
    return get(data,emplurl)
#获取部门信息
def get_dept_info(ticket,yach_dept_ids=[],ehr_dept_ids=[],page=1):
    """
    markdown类型
    :param dept_ids: 部门ID
    :param empl_classes: 员工类型|分隔的员工类型列表，可为空，包括EFU（全职员工）、TFU（全职教师）、TAL（专职教师）、TPA（兼职教师）、EPA（兼职员工）、EPF（在编实习）、EPR（实习生）
    :param empl_ids: 员工ID
    :return: 返回消息发送结果
    """
    emplurl = "https://aom/cmpts/data/account/yach/dept_list"
    data = {
        "per_page": 200,
    }
    data["ticket"] = ticket
    yach_dept_id = '|'.join(set(yach_dept_ids))
    data["yach_dept_id"] = yach_dept_id
    ehr_dept_id = '|'.join(set(ehr_dept_ids))
    data["ehr_dept_id"] = ehr_dept_id
    data["page"] = page
    logging.debug("获取员工信息：%s" % data)
    return get(data,emplurl)
#从数据库获取部门
def getdeps(conn,str):
    DEPTIDS = []
    sql = "SELECT DEPTID FROM `dep_info` where DEPT_DESCR REGEXP %s order by DEPT_DESCR"
    val = (str)
    cursor = conn.cursor()
    try:
        #print 'get status start'
        # 执行sql语句
        cursor.execute(sql,val)
        # 提交到数据库执行
        results = cursor.fetchall()
        for dep in results:
            DEPTID = dep.get('DEPTID')
            if DEPTID is None:
                pass
            else:
                DEPTIDS.append(DEPTID)
    except:
        # Rollback in case there is any error
        print ('select DEPTID fail,rollback')
    return DEPTIDS

#初始设置数据库
def setupdatestatus(conn):
    sql = "update `empl_info` set UPDATE_STATUS = 'false',DLP_STATUS='false'"
    cursor = conn.cursor()
    try:
        #print 'get status start'
        # 执行sql语句
        n = cursor.execute(sql)
        # print n
        # 提交到数据库执行
        conn.commit()
        print ('init impl success')
    except:
        # Rollback in case there is any error
        print ('select DEPTID fail,rollback')
    #print 'aegstatuslist'
    return n

#更新数据库中员工信息
def insertorupdate(conn,ticket, i):
    # dbucloudlist = []
    cursor = conn.cursor()
    EMPLID = i.get('EMPLID')
    highres = get_high(ticket,EMPLID)
    HIGH_LEVEL = None
    #print (highres)
    if highres['data']:
        HIGH_LEVEL = highres['data'].get('C_REPORT_EMPLID')
    #print (HIGH_LEVEL)
    EMPL_RCD = i.get('EMPL_RCD')
    HR_STATUS = 'A'
    DEPTID = i.get('DEPTID')
    DEPT_DESCR = i.get('DEPT_DESCR')
    EMPL_CLASS = i.get('EMPL_CLASS')
    EMPL_CLASS_DESCR = i.get('EMPL_CLASS_DESCR')
    UPDATE_STATUS = 'true'
    # SQL update sql
    sql = "insert into empl_info(EMPLID, EMPL_RCD, HR_STATUS, DEPTID, DEPT_DESCR, EMPL_CLASS,EMPL_CLASS_DESCR,UPDATE_STATUS,HIGH_LEVEL) values(%s,%s,%s,%s,%s,%s,%s,%s,%s) " \
          "on duplicate key update EMPLID=VALUES(EMPLID),EMPL_RCD=VALUES(EMPL_RCD),HR_STATUS=VALUES(HR_STATUS)," \
          "DEPTID=VALUES(DEPTID),DEPT_DESCR=VALUES(DEPT_DESCR),EMPL_CLASS=VALUES(EMPL_CLASS),EMPL_CLASS_DESCR=VALUES(EMPL_CLASS_DESCR),UPDATE_STATUS=VALUES(UPDATE_STATUS),HIGH_LEVEL=VALUES(HIGH_LEVEL)"
    values = (EMPLID, EMPL_RCD, HR_STATUS, DEPTID, DEPT_DESCR, EMPL_CLASS,EMPL_CLASS_DESCR,UPDATE_STATUS,HIGH_LEVEL)
    try:
        # print 'update product sql start'
        # 执行sql语句
        n = cursor.execute(sql, values)
        # print n
        # 提交到数据库执行
        conn.commit()
        #print ('update impl success')
    except Exception as e:
        print (e)
        # Rollback in case there is any error
        conn.rollback()
        print ('update impl fail,rollback')
    sql2 = "update dep_info set DEPT_DESCR = '"+DEPT_DESCR +"' where DEPTID = '" + DEPTID+"'"
    try:
        # print 'update product sql start'
        # 执行sql语句
        m = cursor.execute(sql2)
        # print n
        # 提交到数据库执行
        conn.commit()
        #print ('update impl success')
    except Exception as e:
        print (e)
        # Rollback in case there is any error
        conn.rollback()
        print ('update dep_info DEPT_DESCR fail,rollback')

def updatedept(conn, i):
    # dbucloudlist = []
    cursor = conn.cursor()
    DEPTID = i.get('ehr_dept_id')
    DEPT_DESCR = i.get('name')
    yach_dept_id = i.get('yach_dept_id')
    account_dept_id = i.get('account_dept_id')
    manager_yach_id = i.get('manager_yach_id')
    # SQL update sql
    sql = "insert into dep_info(DEPTID,DEPT_DESCR , yach_dept_id, account_dept_id, manager_yach_id) values(%s,%s,%s,%s,%s) " \
          "on duplicate key update DEPTID=VALUES(DEPTID),DEPT_DESCR=VALUES(DEPT_DESCR),yach_dept_id=VALUES(yach_dept_id)," \
          "account_dept_id=VALUES(account_dept_id),manager_yach_id=VALUES(manager_yach_id)"
    values = (DEPTID, DEPT_DESCR, yach_dept_id, account_dept_id, manager_yach_id)
    try:
        # print 'update product sql start'
        # 执行sql语句
        n = cursor.execute(sql, values)
        # print n
        # 提交到数据库执行
        conn.commit()
        #print ('update dept success')
    except Exception as e:
        print (e)
        print(DEPT_DESCR)
        # Rollback in case there is any error
        conn.rollback()
        print ('update dept fail,rollback')

def checkstr(str):
    if '.' in str:
        return True
    else:
        return False

#更新库中DLP状态
def updatedlpstatus(conn,id):
    sql = "update `empl_info` set DLP_STATUS = 'true' where EMPLID =  %s"
    val = (id)
    cursor = conn.cursor()
    try:
        #print 'get status start'
        # 执行sql语句
        n = cursor.execute(sql,val)
        # print n
        # 提交到数据库执行
        conn.commit()
        #print ('update dlpstatus success')
    except Exception as e:
        print (e)
        # Rollback in case there is any error
        print ('update dlpstatus fail,rollback')

#获取未安装DLP员工
def getimpls(conn):
    EMPLIDS = []
    sql = "SELECT EMPLID FROM `empl_info` where DLP_STATUS = 'false' and NEED_STATUS='yes' and UPDATE_STATUS = 'true'"
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        results = cursor.fetchall()
        for dep in results:
            EMPLID = dep.get('EMPLID')
            EMPLIDS.append(EMPLID)
            sql2 = "update `empl_info` set TIMES=TIMES+1 WHERE EMPLID= "+EMPLID
            try:
                # print 'get status start'
                # 执行sql语句
                n = cursor.execute(sql2)
                # print n
                # 提交到数据库执行
                conn.commit()
                #print ('update TIMES success')
            except Exception as e:
                print (e)
                # Rollback in case there is any error
                print ('update TIMES fail,rollback')
    except:
        # Rollback in case there is any error
        print ('select EMPLID fail,rollback')
    #print (EMPLIDS)
    return EMPLIDS

#获取已安装DLP员工
def getinstalls(conn,str):
    EMPLIDS = []
    sql = "SELECT EMPLID FROM `empl_info` where DLP_STATUS = 'true' and NEED_STATUS='yes' and UPDATE_STATUS = 'true' and DEPT_DESCR REGEXP %s"
    val = (str)
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql,val)
        # 提交到数据库执行
        results = cursor.fetchall()
        for dep in results:
            EMPLID = dep.get('EMPLID')
            EMPLIDS.append(EMPLID)
    except:
        # Rollback in case there is any error
        print ('select EMPLID fail,rollback')
    #print (EMPLIDS)
    return EMPLIDS

#获取白名单员工
def getwhite(conn,str):
    EMPLIDS = []
    sql = "SELECT EMPLID FROM `empl_info` where NEED_STATUS='no' and UPDATE_STATUS = 'true' and DEPT_DESCR REGEXP %s"
    val = (str)
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql,val)
        # 提交到数据库执行
        results = cursor.fetchall()
        for dep in results:
            EMPLID = dep.get('EMPLID')
            EMPLIDS.append(EMPLID)
    except:
        # Rollback in case there is any error
        print ('select EMPLID fail,rollback')
    #print (EMPLIDS)
    return EMPLIDS

#设置白名单员工
def setwhite(conn,id):
    sql = "update `empl_info` set NEED_STATUS='no' where DEPTID =  %s"
    val = (id)
    cursor = conn.cursor()
    try:
        #print 'get status start'
        # 执行sql语句
        n = cursor.execute(sql,val)
        # print n
        # 提交到数据库执行
        conn.commit()
        #print ('update dlpstatus success')
    except Exception as e:
        print (e)
        # Rollback in case there is any error
        print ('set dlpwhite fail,rollback')

# 设置白名单员工
def setstrwhite(conn, str):
    sql = "update `empl_info` set NEED_STATUS='no' where DEPT_DESCR REGEXP %s"
    val = (str)
    cursor = conn.cursor()
    try:
        # print 'get status start'
        # 执行sql语句
        n = cursor.execute(sql, val)
        # print n
        # 提交到数据库执行
        conn.commit()
        # print ('update dlpstatus success')
    except Exception as e:
        print (e)
        # Rollback in case there is any error
        print ('set dlpwhite fail,rollback')


#检查员工是否安装DLP
def checkinstall(conn,id):
    sql = "SELECT EMPLID FROM `empl_info` where DLP_STATUS = 'true' and NEED_STATUS='yes' and UPDATE_STATUS = 'true' and EMPLID = %s"
    val = (id)
    cursor = conn.cursor()
    try:
        # 执行sql语句
        count = cursor.execute(sql,val)
        # 提交到数据库执行
        if count>0:
            return True
        else:
            return False
    except:
        # Rollback in case there is any error
        print ('select EMPLID fail,rollback')

#获取未安装DLP员工上级
def gethighs(conn):
    EMPLIDS = []
    sql = "SELECT HIGH_LEVEL FROM `empl_info` where DLP_STATUS = 'false' and NEED_STATUS='yes' and UPDATE_STATUS = 'true'"
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        results = cursor.fetchall()
        for dep in results:
            EMPLID = dep.get('HIGH_LEVEL')
            EMPLIDS.append(EMPLID)
    except:
        # Rollback in case there is any error
        print ('select EMPLID fail,rollback')
    #print (len(EMPLIDS))
    return set(EMPLIDS)

#获取未安装DLP员工下级
def getlows(conn,high):
    EMPLIDS = []
    sql = "SELECT EMPLID FROM `empl_info` where DLP_STATUS = 'false' and NEED_STATUS='yes' and UPDATE_STATUS = 'true' and HIGH_LEVEL = " + high
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        results = cursor.fetchall()
        for dep in results:
            EMPLID = dep.get('EMPLID')
            EMPLIDS.append(EMPLID)
    except:
        # Rollback in case there is any error
        print ('select EMPLID fail,rollback')
    #print (len(EMPLIDS))
    return set(EMPLIDS)

#更新部门人数
def updatesum(conn,sum,id):
    sql = "update `dep_info` set sum = '%s' where DEPTID =  %s"
    val = (sum,id)
    cursor = conn.cursor()
    try:
        #print 'get status start'
        # 执行sql语句
        n = cursor.execute(sql,val)
        # print n
        # 提交到数据库执行
        conn.commit()
        #print ('update dlpstatus success')
    except Exception as e:
        print (e)
        # Rollback in case there is any error
        print ('update sum fail,rollback')

#更新部门已安装人数,白名单人数
def updateinstall(conn,sum,wsum,id):
    sql = "update `dep_info` set install = '%s',white= '%s' where DEPTID = %s"
    val = (sum,wsum,id)
    cursor = conn.cursor()
    try:
        #print 'get status start'
        # 执行sql语句
        n = cursor.execute(sql,val)
        # print n
        # 提交到数据库执行
        conn.commit()
        #print ('update dlpstatus success')
    except Exception as e:
        print (e)
        # Rollback in case there is any error
        print ('update sum fail,rollback')

#获取人数及比例
def getnums(conn,id):
    sql = "select sum,install,white,DEPT_DESCR from `dep_info`  where DEPTID =  %s"
    val = (id)
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql,val)
        # 提交到数据库执行
        results = cursor.fetchall()
        return results
    except Exception as e:
        print (e)
        # Rollback in case there is any error
        print ('select num fail,rollback')

#获取count
def getcount(conn,str):
    count = 0
    sql = "SELECT count(*) FROM `empl_info` where DEPT_DESCR REGEXP %s"
    val = (str)
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.execute(sql,val)
        # 提交到数据库执行
        results = cursor.fetchall()
        print(results)
        for dep in results:
            count = dep.get('count(*)')
            print(count)
    except:
        # Rollback in case there is any error
        print ('select count fail,rollback')
    #print (EMPLIDS)
    return count


def is_not_null_and_blank_str(content):
    """
    非空字符串
    :param content: 字符串
    :return: 非空 - True，空 - False

    >>> is_not_null_and_blank_str('')
    False
    >>> is_not_null_and_blank_str(' ')
    False
    >>> is_not_null_and_blank_str('  ')
    False
    >>> is_not_null_and_blank_str('123')
    True
    """
    if content and content.strip():
        return True
    else:
        return False


class DingtalkChatbot(object):
    """
    钉钉工作通知，给同一用户发相同内容消息一天仅允许一次。给同一用户发消息一天不得超过50次。
    """
    def __init__(self):
        """
        机器人初始化
        """
        super(DingtalkChatbot, self).__init__()
        self.times = 0
        self.start_time = time.time()
        self.webhook = "https://aom/message/ding_notice"
        self.yachhook = "https://am/cmpts/msgchl/yach/notice/send"

    def send_text(self, webhook,msg, is_at_all=False, at_mobiles=[]):
        """
        text类型
        :param msg: 消息内容
        :param is_at_all: @所有人时：true，否则为false
        :param at_mobiles: 被@人的手机号（字符串）
        :return: 返回消息发送结果
        """
        data = {"msgtype": "text"}
        if is_not_null_and_blank_str(msg):
            data["text"] = {"content": msg}
        else:
            logging.error("text类型，消息内容不能为空！")
            raise ValueError("text类型，消息内容不能为空！")

        if at_mobiles:
            at_mobiles = list(map(str, at_mobiles))

        data["at"] = {"atMobiles": at_mobiles, "isAtAll": is_at_all}
        logging.debug('text类型：%s' % data)
        return post(json.dumps(data),webhook)


    def send_yach_text(self, msg,user_type, at_users=[],at_dept_ids=[]):
        """
        text类型
        :param msg: 消息内容
        :param user_type:  	用户类型，支持account_id、email、workcode、yachid
        :param at_users:  	员工，数据类型匹配user_type参数，多值使用|分隔，最多允许100个值
        :param at_dept_ids:  	yach部门id，多值使用|分隔，最多允许20个值，(自动包括子部门)
        :return: 返回消息发送结果
        """
        if is_not_null_and_blank_str(msg) and is_not_null_and_blank_str(user_type):
            if at_users or at_dept_ids:
                message = {"msgtype": "text"}
                message["text"] = {"content": msg}
                data = {"message": base64.b64encode(json.dumps(message).encode('utf-8'))}
                users = '|'.join(set(at_users))
                data["userid_list"] = users
                dept_id_list = '|'.join(set(at_dept_ids))
                data["dept_id_list"] = dept_id_list
                data["user_type"] = user_type
                ticket = getticket()
                data["ticket"] = ticket
            else:
                logging.error("发送人不能为空！")
                raise ValueError("发送人不能为空不能为空！")
        else:
            logging.error("text类型，消息内容不能为空！")
            raise ValueError("text类型，消息内容不能为空！")
        logging.debug('text类型：%s' % data)
        return post(data,self.yachhook)


    def send_yach_markdown(self,ticket, title, text,user_type=None, image=None,at_users=[],at_dept_ids=[]):
        """
        markdown类型
        :param user_type:  	用户类型，支持account_id、email、workcode、yachid
        :param at_users:  	员工，数据类型匹配user_type参数，多值使用|分隔，最多允许100个值
        :param at_dept_ids:  	yach部门id，多值使用|分隔，最多允许20个值，(自动包括子部门)
        :return: 返回消息发送结果
        """
        if is_not_null_and_blank_str(title) and is_not_null_and_blank_str(text):
            if at_users or at_dept_ids:
                if image:
                    message = {
                        "msgtype": "markdown",
                        "markdown": {
                            "title": title,
                            "text": text,
                            "image": image
                        },
                    }
                else:
                    message = {
                        "msgtype": "markdown",
                        "markdown": {
                            "title": title,
                            "text": text
                        },
                    }
                data = {"message": base64.b64encode(json.dumps(message).encode('utf-8'))}
                users = '|'.join(set(at_users))
                data["userid_list"] = users
                dept_id_list = '|'.join(set(at_dept_ids))
                data["dept_id_list"] = dept_id_list
                data["user_type"] = user_type
                data["ticket"] = ticket
            else:
                logging.error("发送人不能为空！")
                raise ValueError("发送人不能为空不能为空！")
        else:
            logging.error("markdown类型中消息标题或内容不能为空！")
            raise ValueError("markdown类型中消息标题或内容不能为空！")
        logging.debug("markdown类型：%s" % data)
        return post(data, self.yachhook)


if __name__ == '__main__':
    xiaoding = DingtalkChatbot()
    ticket = getticket()
    conn = getmysqlconn()
    empl_classes=['EPR','EFU']
    yachurl = 'https://u.com/robot/send?access_token=UVk0MkMDlleg'
    secret = 'SEC65e8db562'
    timestamp = int(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.request.quote(base64.b64encode(hmac_code))
    webhook = yachurl + "&timestamp=" + str(timestamp) + "&sign=" + sign


    # ######获取人员信息，获取部门，调试代码
    # ids=['121450','145418','066210','003092']  #老大的workcode
    # #deps =  ['D1011688']
    # #dept_ids = ['D1006924'] 
    # info = get_empl_info(ticket,empl_ids=ids,main='all')
    # print (info)
    # #info = get_empl_info(ticket,dept_ids=deps)
    # #print (info)
    # # print (get_high(ticket,'113125'))



    ###获取所有部门
    countdep = 200
    pagedep = 1
    while (countdep==200):
        deptlistresponse = get_dept_info(ticket, page=pagedep)
        print (deptlistresponse)
        deptlist = deptlistresponse['data']['list']
        countdep = len(deptlist)
        for i in deptlist:
            updatedept(conn,i)
        pagedep=pagedep+1

    #####初始化数据库，设置全员离职与未安装
    n=setupdatestatus(conn)
    # ###获取所有人
    depts = []
    depts.append('D1000002')  
    depts.append('D1014111')  
    depts.append('D1022424')  
    depts.append('D1006598')
    depts.append('D1006603')
    depts.append('D1006602')
    depts.append('D1006601')
    depts.append('D1010856')
    depts.append('D1011688')

    print (depts)
    for d in depts:
        allemplcount = 100
        allemplpage = 1
        while (allemplcount == 100):
            allemplresponse = get_empl_info(ticket, dept_ids=[d], empl_classes=empl_classes, page=allemplpage)
            print (allemplresponse)
            userlist = allemplresponse['data']['list']
            allemplcount = len(userlist)
            for i in userlist:
                insertorupdate(conn, ticket, i)
            allemplpage = allemplpage + 1
        total = allemplresponse['data']['total']
        print (total)
        updatesum(conn, total, d)
    ####统计人数，查漏补缺
    countdict = {}
    countdict.update({'D1001112':'事业部'})
    for i in list(countdict.keys()):
        count = getcount(conn,countdict.get(i))
        updatesum(conn, count, i)



    # ##表格处理方法,更新安装状态
    csvfile = open('client_device_all.csv', newline='')
    # ###获得对象
    csvReader = csv.reader(csvfile)
    # ###获得标题，下面读取就不读取标题了
    headers = next(csvReader)
    # ###读取内容并打印
    for row in csvReader:
        # print(row)
        name = row[0]
        if checkstr(name):
            id = name.split(".")[1]
            #print (id)
            updatedlpstatus(conn,id)
    # ###关闭。这个经常有小伙伴忘了，今天在群里就有人遇到这个问题了
    csvfile.close()
    print ('file done')


    ######福利员工白名单
    ######设置单个部门，整个部门，按ID
    whitelistdep = []
    whitelistdep.append('D1010704') # D1010704  福利员工部
    for w in whitelistdep:
        setwhite(conn, w)
    ########设置总部门，按字符串
    addwhitedict = {}
    for i in list(addwhitedict.keys()):
        setstrwhite(conn,addwhitedict.get(i))

    # ###计算大的部门统计数据，入库
    whitedict = {}
    whitedict.update({'D1000002':'集团总部'})
    whitedict.update({'D1014111':'用户中台'})
    whitedict.update({'D1022424':'数据中台'})
    whitedict.update({'D1001112':'事业部'})
    print (whitedict)
    for i in list(whitedict.keys()):
        whiteempl = getwhite(conn, whitedict.get(i))
        installed = getinstalls(conn,whitedict.get(i))
        updateinstall(conn, len(installed), len(whiteempl), i)

    # ###按需求计算小的统计数据入库
    #### 前提是提前设置好dep表的描述
    regdict ={}
    regdict.update({'集团总部':'集团总部-[^-]+-[^-]+$'})
    regdict.update({'用户中台':'用户中台$'})
    regdict.update({'数据中台':'数据中台$'})
    regdict.update({'事业部':'事业部-[^-]+$'})
    for r in list(regdict.keys()):
        whiteempl = getwhite(conn, r)
        installed = getinstalls(conn,r)
        deplist = getdeps(conn,regdict.get(r))  #sql语句为定制
        print (deplist)
        for d in deplist:
            depempllist = []
            usercount = 100
            userpage = 1
            while (usercount == 100):
                pageempllist = get_empl_info(ticket, dept_ids=[d], empl_classes=empl_classes, page=userpage)
                print (pageempllist)
                pageuserlist = pageempllist['data']['list']
                usercount = len(pageuserlist)
                for i in pageuserlist:
                    EMPLID = i.get('EMPLID')
                    depempllist.append(EMPLID)
                userpage = userpage + 1
            total = pageempllist['data']['total']
            print (total)
            updatesum(conn,total,d)
            s = set(installed)  #已安装全量列表
            t = set(depempllist)  #部门全量列表
            w = set(whiteempl)  #白名单全量列表
            b = t & s   #部门已安装列表
            c = t & w   #部门白名单列表
            updateinstall(conn,len(b),len(c),d)
            print (d+"完成")


    ####获取通知发送
    empl_ids = getimpls(conn)
    #print (empl_ids)
    tongzhi = "本次通知人数为"+str(len(empl_ids))
    print (tongzhi)
    msg =  '通知已发送，统计详情如下：\n'+tongzhi+'\n'
    noticelist = list_split(empl_ids, 90)
    imgurl = "http://oom/upload/images/安装提醒.png"
    title="DLP安装提醒"
    text="老师，您好：\n  \n 后台检测到您没有安装数据防泄露软件(简称DLP)。集团发布了相关红线。\n " \
         "**《集团信息安全红线和处罚规定》第十条明确：业务负责人对员工不安装终端DLP或私自卸载的行为承担连带责任。如果您不安装，您的领导将承担连带责任。** \n " \
         "DLP安装说明请访问如下链接：\n [使用点击查看](https://ylou.com/docs/f6e8311fe6b64eed/) \n 温馨提示：安装并且绑定域用户才算安装完成。如果您未绑定，您会持续收到此消息"
    for i in noticelist:
        print (i)
        response =xiaoding.send_yach_markdown(ticket,title,text,image=imgurl,user_type='workcode',at_users=i)
        print (response)

    high = gethighs(conn)
    print ('本次通知上级人数为'+str(len(high)))
    imgurl = "http://om/upload/images/安装提醒.png"
    title="DLP安装提醒"
    for i in high:
        lows = getlows(conn,i)
        txt = "老师您好，根据集团总部要求，员工需要自行安装办公电脑的数据防泄露软件，通知以来，目前您部门还有 "+str(len(lows))+" 位老师未按要求进行安装 ，工号分别是"+str(lows)+"，需要您督促其尽快完成安装。集团总部截止时间为2020.5.31。技术中台截止时间为2020.6.14。有问题按照链接内容进群反馈。"
        response = xiaoding.send_yach_markdown(ticket, title, txt, image=imgurl, user_type='workcode', at_users=[i])
        print (response)
    # #



    ####按统计需求发送汇总
    depdict = {}
    depdict.update({'D1000002':'集团总部-[^-]+-[^-]+$'})
    depdict.update({'D1014111':'用户中台$'})
    depdict.update({'D1022424':'数据中台$'})
    depdict.update({'D1001112':'事业部-[^-]+$'})
    for i in list(depdict.keys()):
        msg1 = ''
        deplist = getdeps(conn,depdict.get(i))
        deplist.append(i)
        for dep in deplist:
            result = getnums(conn,dep)
            for i in result:
                sum = i.get('sum')
                install = i.get('install')
                white = i.get('white')
                DEPT_DESCR = i.get('DEPT_DESCR')
                need = int(sum)-int(white)
                if need:
                    percentp = '{:.2%}'.format(float(install) / float(need))
                    msgp =DEPT_DESCR+' 总人数为 '+sum+'，白名单人数为 '+white+'，已安装人数为 '+install+'，安装比例为'+percentp+'\n'
                else:
                    msgp =  DEPT_DESCR+' 需要安装人数为0\n'
                msg1 = msg1 + msgp
        print (msg1)
        response = xiaoding.send_text(webhook,msg+msg1, is_at_all=True)
        print (response)




    #### 随时根据需求获取部门数据，安装人数及未安装人数
    sql = "select EMPLID,DEPT_DESCR from empl_info where DEPT_DESCR REGEXP '数据中台' and  DLP_STATUS = 'false' and NEED_STATUS='yes' and UPDATE_STATUS = 'true'"
    sql = "select * from dep_info where DEPT_DESCR REGEXP '办公室'"







