#! /usr/bin/env python
# _*_ coding:utf-8 _*_

import base64
import json
import logging
from urlparse import urlparse
import time
import requests
from datetime import datetime, timedelta
import MySQLdb.cursors
import MySQLdb as mdb
import hmac
import hashlib
import base64
import urllib
import json

app_id = '13603'
app_key = 'yNo0h'

session = requests.session()

def list_split(items, n):
    return [items[i:i+n] for i in range(0, len(items), n)]


# def getmysqlconn():
#    config = {
#        'host': '10..1',
#        'port': 3306,
#        'user': 'root',
#        'passwd': 'tq1',
#        'db': 'ops',
#        'charset': 'utf8',
#        'cursorclass': MySQLdb.cursors.DictCursor
#    }
#    conn = mdb.connect(**config)
#    return conn

def getmysqlconn():
    config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'ops',
        'passwd': '0m',
        'db': 'ops',
        'charset': 'utf8',
        'cursorclass': MySQLdb.cursors.DictCursor
    }
    conn = mdb.connect(**config)
    return conn


headers = {'Content-Type': 'application/json; charset=utf-8'}

def get(data,webhook):
    """
    发送消息（内容UTF-8编码）
    :param data: 消息数据（字典）
    :return: 返回发送结果
    """
    param = urllib.urlencode(data)
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
    ticket_url = "http://apom/basic/get_ticket"
    response = get(data,ticket_url)
    print (response)
    if response and response['errcode'] == 0:
        ticket = response['ticket']
    else:
        print ("获取ticket失败")
    return ticket

def checkstr(str):
    if '.' in str:
        return True
    else:
        return False

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

def getorderlist(conn,id):
#    sql = 'select id  from ops_hole where level =2 and business_id=16'
    sql = 'select ops_hole.title,ops_hole.level,ops_order.step,ops_order.exptime,ops_order.order_id from ops_order,ops_hole where ops_order.hole_id=ops_hole.id and is_expired=1 and step!=4 and business_id='+str(id)
    print sql
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchall()
    #print results
    #print results.__class__
    print 'get order success'
        #print holelist
    # except:
    #     # Rollback in case there is any error
    #     print 'select hole dict fail,rollback'
    return results

def getemail(conn,id):
    sql = 'select ops_user.email,ops_business.mgr_ids from ops_user,ops_business where ops_user.id=ops_business.mgr_ids and ops_business.id='+str(id) #+' order by exptime desc'
    print sql
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchone()
    email = results.get('email')
    print 'get user success'
    # except:
    #     # Rollback in case there is any error
    #     print 'select webhook fail,rollback'
    return email

def gettopemail(conn,id):
    sql = 'select ops_user.email,ops_business.topmanagerid from ops_user,ops_business where ops_user.id=ops_business.topmanagerid and ops_business.id='+str(id) #+' order by exptime desc'
    print sql
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchone()
    topemail = results.get('email')
    print 'get user success'
    # except:
    #     # Rollback in case there is any error
    #     print 'select webhook fail,rollback'
    return topemail


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
        self.webhook = "https://aal.com/message/ding_notice"
        self.yachhook = "https://aal.com/cmpts/msgchl/yach/notice/send"

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
    leveldict ={2:'高危',1:'中危',0:'低危'}
    ops = 'http://ol.com/admin/order/step'
    title = "漏洞过期未修复提醒"
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    lastweek = (datetime.now() - timedelta(weeks=1)).strftime("%Y-%m-%d")
    lastmonth = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    print(lastweek,lastmonth)


    try:
        # 循环部门
        for i in range(1,200,1):
            print i
            msg = ''
            topmsg = ''
            emaillist = []
            topemaillist = []
            orderlist = getorderlist(conn, i)
            if orderlist:
                email = getemail(conn, i)
                emaillist.append(email)
                print emaillist

                topemail = gettopemail(conn, i)
                topemaillist.append(topemail)
                print topemaillist
                for h in orderlist:
                    msgp = ''
                    topmsgp = ''
                    print h
                    name = h.get('title')
                    level = h.get('level')
                    order_id = h.get('order_id')
                    step = h.get('step')
                    exptime = h.get('exptime').strftime("%Y-%m-%d")
                    url = ops + str(step) + '?id=' + str(order_id)

                    print  exptime
                    if lastweek>exptime:
                        print "过期一周"
                        msgp = "[" + str(order_id) + "](" + url + ")" + "，"
                        msg = msg + msgp

                    if lastmonth>exptime:
                        print "过期一月"
                        topmsgp = "[" + str(order_id) + "](" + url + ")" + "，"
                        topmsg = topmsg + topmsgp

                if msg:
                    txt = "老师您好，您的业务线存在"+ str(len(orderlist))+"个过期未修复漏洞。过期一周的工单列表如下：\n"+msg+"\n 请尽快到[工单系统](https://ocom/admin/order/list)修复！\n 如漏洞过期一个月，会通知到事业部总经理。"
                    response = xiaoding.send_yach_markdown(ticket, title, txt, user_type='email',at_users=emaillist)
                    print (response)
                if topmsg:
                    toptxt = "老师您好，您的业务线存在"+ str(len(orderlist))+"个过期未修复漏洞。过期一月的工单列表如下：\n"+topmsg+"\n 请尽快到[工单系统](https://oom/admin/order/list)修复！\n 此漏洞已过期一个月，烦请事业部总经理推动修复。"
                    topresponse = xiaoding.send_yach_markdown(ticket, title, toptxt, user_type='email',at_users=topemaillist)
                    print (topresponse)


    except Exception as e:
        yachurl = 'https://yau.com/robot/send?access_token=OHplrVVpJcUNIKw'
        yachsecret = 'SE20a79e9'
        timestamp = long(round(time.time() * 1000))
        secret_enc = bytes(yachsecret).encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, yachsecret)
        string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.quote_plus(base64.b64encode(hmac_code))
        # print(timestamp)
        # print(sign)
        webhook = yachurl + "&timestamp=" + str(timestamp) + "&sign=" + sign
        response = xiaoding.send_text(webhook,'ops_expired'+str(e) + '@1371', at_mobiles=['137573'])
        print (response)



