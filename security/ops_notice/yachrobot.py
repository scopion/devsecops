#! /usr/bin/env python
# _*_ coding:utf-8 _*_

import requests
import json
import sys,datetime
import requests
import MySQLdb.cursors
import MySQLdb as mdb
import time
import re
#from json import JSONDecodeError
import logging
import requests
import time
import hmac
import hashlib
import base64
import urllib
import json
import sys
import MySQLdb.cursors
import MySQLdb as mdb
import re
#from json import JSONDecodeError
import logging
import requests
import time
from datetime import datetime,timedelta

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
    钉钉群自定义机器人（每个机器人每分钟最多发送20条），支持文本（text）、连接（link）、markdown三种消息类型！
    """
    def __init__(self, webhook):
        """
        机器人初始化
        :param webhook: 钉钉群自定义机器人webhook地址
        """
        super(DingtalkChatbot, self).__init__()
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.times = 0
        self.start_time = time.time()
        self.webhook = webhook


    def send_text(self, msg, is_at_all=False, at_mobiles=[]):
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
        return self.post(data)

    def send_link(self, title, text, message_url, pic_url=''):
        """
        link类型
        :param title: 消息标题
        :param text: 消息内容（如果太长自动省略显示）
        :param message_url: 点击消息触发的URL
        :param pic_url: 图片URL
        :return: 返回消息发送结果

        """
        if is_not_null_and_blank_str(title) and is_not_null_and_blank_str(text) and is_not_null_and_blank_str(message_url):
            data = {
                    "msgtype": "link",
                    "link": {
                        "text": text,
                        "title": title,
                        "picUrl": pic_url,
                        "messageUrl": message_url
                    }
            }
            logging.debug('link类型：%s' % data)
            return self.post(data)
        else:
            logging.error("link类型中消息标题或内容或链接不能为空！")
            raise ValueError("link类型中消息标题或内容或链接不能为空！")

    def send_markdown(self, title, text, is_at_all=False, at_mobiles=[]):
        """
        markdown类型
        :param title: 首屏会话透出的展示内容
        :param text: markdown格式的消息内容
        :param is_at_all: 被@人的手机号（在text内容里要有@手机号）
        :param at_mobiles: @所有人时：true，否则为：false
        :return: 返回消息发送结果
        """
        if is_not_null_and_blank_str(title) and is_not_null_and_blank_str(text):
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text
                },
                "at": {
                    "atMobiles": list(map(str, at_mobiles)),
                    "isAtAll": is_at_all
                }
            }
            logging.debug("markdown类型：%s" % data)
            return self.post(data)
        else:
            logging.error("markdown类型中消息标题或内容不能为空！")
            raise ValueError("markdown类型中消息标题或内容不能为空！")

    def send_action_card(self, action_card):
        """
        ActionCard类型
        :param action_card: 整体跳转ActionCard类型实例或独立跳转ActionCard类型实例
        :return: 返回消息发送结果
        """
        if isinstance(action_card, ActionCard):
            data = action_card.get_data()
            logging.debug("ActionCard类型：%s" % data)
            return self.post(data)
        else:
            logging.error("ActionCard类型：传入的实例类型不正确！")
            raise TypeError("ActionCard类型：传入的实例类型不正确！")

    def send_feed_card(self, links):
        """
        FeedCard类型
        :param links: 信息集（FeedLink数组）
        :return: 返回消息发送结果
        """
        link_data_list = []
        for link in links:
            if isinstance(link, FeedLink) or isinstance(link, CardItem):
                link_data_list.append(link.get_data())
        if link_data_list:
            # 兼容：1、传入FeedLink或CardItem实例列表；2、传入数据字典列表；
            links = link_data_list
        data = {"msgtype": "feedCard", "feedCard": {"links": links}}
        logging.debug("FeedCard类型：%s" % data)
        return self.post(data)

    def post(self, data):
        """
        发送消息（内容UTF-8编码）
        :param data: 消息数据（字典）
        :return: 返回发送结果
        """
        self.times += 1
        if self.times % 20 == 0:
            if time.time() - self.start_time < 60:
                logging.debug('钉钉官方限制每个机器人每分钟最多发送20条，当前消息发送频率已达到限制条件，休眠一分钟')
                time.sleep(60)
            self.start_time = time.time()

        post_data = json.dumps(data)
        try:
            print self.webhook
            print post_data
            response = requests.post(self.webhook, headers=self.headers, data=post_data)
            print response.text
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
                logging.debug('发送结果：%s' % result)
                if result['code']!=200:
                    error_data = {"msgtype": "text", "text": {"content": "钉钉机器人消息发送失败，原因：%s" % result['msg']}, "at": {"isAtAll": True}}
                    logging.error("消息发送失败，自动通知：%s" % error_data)
                    requests.post(self.webhook, headers=self.headers, data=json.dumps(error_data))
                return result


class ActionCard(object):
    """
    ActionCard类型消息格式（整体跳转、独立跳转）
    """
    def __init__(self, title, text, btns, btn_orientation=0, hide_avatar=0):
        """
        ActionCard初始化
        :param title: 首屏会话透出的展示内容
        :param text: markdown格式的消息
        :param btns: 按钮列表类型；
                     按钮数量为1时，整体跳转ActionCard类型，按钮的消息：singleTitle - 单个按钮的方案，singleURL - 点击按钮触发的URL；
                     按钮数量大于1时，独立跳转ActionCard类型，按钮的消息：title - 按钮方案，actionURL - 点击按钮触发的URL；
        :param btn_orientation: 0：按钮竖直排列，1：按钮横向排列
        :param hide_avatar: 0：正常发消息者头像，1：隐藏发消息者头像
        """
        super(ActionCard, self).__init__()
        self.title = title
        self.text = text
        self.btn_orientation = btn_orientation
        self.hide_avatar = hide_avatar
        btn_list = []
        for btn in btns:
            if isinstance(btn, CardItem):
                btn_list.append(btn.get_data())
        if btn_list:
            # 兼容：1、传入CardItem示例列表；2、传入数据字典列表
            btns = btn_list
        self.btns = btns

    def get_data(self):
        """
        获取ActionCard类型消息数据（字典）
        :return: 返回ActionCard数据
        """
        if is_not_null_and_blank_str(self.title) and is_not_null_and_blank_str(self.text) and len(self.btns):
            if len(self.btns) == 1:
                # 独立跳转
                data = {
                        "msgtype": "actionCard",
                        "actionCard": {
                            "title": self.title,
                            "text": self.text,
                            "hideAvatar": self.hide_avatar,
                            "btnOrientation": self.btn_orientation,
                            "singleTitle": self.btns[0]["title"],
                            "singleURL": self.btns[0]["actionURL"]
                        }
                }
                return data
            else:
                # 整体跳转
                data = {
                    "msgtype": "actionCard",
                    "actionCard": {
                        "title": self.title,
                        "text": self.text,
                        "hideAvatar": self.hide_avatar,
                        "btnOrientation": self.btn_orientation,
                        "btns": self.btns
                    }
                }
                return data
        else:
            logging.error("ActionCard类型，消息标题或内容或按钮数量不能为空！")
            raise ValueError("ActionCard类型，消息标题或内容或按钮数量不能为空！")


class FeedLink(object):
    """
    FeedCard类型单条消息格式
    """
    def __init__(self, title, message_url, pic_url):
        """
        初始化单条消息文本
        :param title: 单条消息文本
        :param message_url: 点击单条信息后触发的URL
        :param pic_url: 点击单条消息后面图片触发的URL
        """
        super(FeedLink, self).__init__()
        self.title = title
        self.message_url = message_url
        self.pic_url = pic_url

    def get_data(self):
        """
        获取FeedLink消息数据（字典）
        :return: 本FeedLink消息的数据
        """
        if is_not_null_and_blank_str(self.title) and is_not_null_and_blank_str(self.message_url) and is_not_null_and_blank_str(self.pic_url):
            data = {
                    "title": self.title,
                    "messageURL": self.message_url,
                    "picURL": self.pic_url
            }
            return data
        else:
            logging.error("FeedCard类型单条消息文本、消息链接、图片链接不能为空！")
            raise ValueError("FeedCard类型单条消息文本、消息链接、图片链接不能为空！")


class CardItem(object):
    """
    ActionCard和FeedCard消息类型中的子控件
    """

    def __init__(self, title, url, pic_url=None):
        """
        CardItem初始化
        @param title: 子控件名称
        @param url: 点击子控件时触发的URL
        @param pic_url: FeedCard的图片地址，ActionCard时不需要，故默认为None
        """
        super(CardItem, self).__init__()
        self.title = title
        self.url = url
        self.pic_url = pic_url

    def get_data(self):
        """
        获取CardItem子控件数据（字典）
        @return: 子控件的数据
        """
        if is_not_null_and_blank_str(self.pic_url) and is_not_null_and_blank_str(self.title) and is_not_null_and_blank_str(self.url):
            data = {
                "title": self.title,
                "messageURL": self.url,
                "picURL": self.pic_url
            }
            return data
        elif is_not_null_and_blank_str(self.title) and is_not_null_and_blank_str(self.url):
            data = {
                "title": self.title,
                "actionURL": self.url
            }
            return data
        else:
            logging.error("CardItem是ActionCard的子控件时，title、url不能为空；是FeedCard的子控件时，title、url、pic_url不能为空！")
            raise ValueError("CardItem是ActionCard的子控件时，title、url不能为空；是FeedCard的子控件时，title、url、pic_url不能为空！")



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

def getholeidlist(conn,id):
    listhole = []
#    sql = 'select id  from ops_hole where level =2 and business_id=16'
    sql = 'select id,title,level  from ops_hole where business_id='+str(id)
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
    for p in results:
        #print p
        listhole.append(p)
    print 'get hole success'
        #print holelist
    # except:
    #     # Rollback in case there is any error
    #     print 'select hole dict fail,rollback'
    return listhole

def getorder(conn,hole_id):
    sql = 'select order_id,step,exptime,create_time  from ops_order where step<3 and hole_id='+str(hole_id) #+' order by exptime desc'
    #print sql
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchone()
    print 'get order success'
    # except:
    #     # Rollback in case there is any error
    #     print 'select order fail,rollback'
    return results

def getwebhook(conn,id):
    webhook = None
    sql = 'select yachurl,yachsecret  from ops_business where id='+str(id) #+' order by exptime desc'
    print sql
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchone()
    if results:
        yachurl = results.get('yachurl')
        yachsecret  = results.get('yachsecret')
        timestamp = long(round(time.time() * 1000))
        secret_enc = bytes(yachsecret).encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, yachsecret)
        string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.quote_plus(base64.b64encode(hmac_code))
        # print(timestamp)
        # print(sign)
        if yachurl and yachsecret:
            webhook = yachurl + "&timestamp=" + str(timestamp) + "&sign=" + sign
    print 'get webhook success'
    # except:
    #     # Rollback in case there is any error
    #     print 'select webhook fail,rollback'
    return webhook



if __name__ == '__main__':
    try:
        conn = getmysqlconn()
        leveldict ={2:'高危',1:'中危',0:'低危'}
        url = 'http://ol.com/admin/order/step'
        shareurl = 'http://ol.com/admin/order/preview'
        sharenow = datetime.now()
        sharetomorrow = sharenow + timedelta(hours=8)
        timeamp = time.mktime(sharetomorrow.timetuple())
        exp = int(timeamp)
        #    url = 'http://ol.com/admin/order/step'3?id=2751
        now = time.strftime("%H:%M")
        #print now
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        #print tomorrow

        # WebHook地址
        for i in range(1,200,1):
            print i
            msg = '从2020.12月起，漏洞过期一周会通知到研发负责人\n'
            msg1 = ''
            webhook = getwebhook(conn,i)
            if webhook:
                print webhook
                holelist = getholeidlist(conn, i)
                if holelist:
                    print holelist
                    for h in holelist:
                        #print h
                        id = h.get('id')
                        orderdict = getorder(conn, id)
                        if orderdict:
                            #print hook
                            print orderdict
                            title = h.get('title')
                            level = h.get('level')
                            order_id = orderdict.get('order_id')
                            step = orderdict.get('step')
                            exptime = orderdict.get('exptime').strftime("%Y-%m-%d")
                            create_time = orderdict.get('create_time').strftime("%Y-%m-%d")

                            #print exptime
                            #print tomorrow
                            msgp = ''
                            msgp1 = ''
                            if now > '16:00':
                                if create_time == today:
                                    msgp1 = '今日新增' + leveldict.get(level) + '漏洞，过期时间为:' + str(exptime) + '\n' + '摘要：' + title.encode("utf-8") + '\n' + '链接:' + url + str(step) + '?id=' + str(order_id) + '\n'
                                if exptime == tomorrow:
                                    msgp = leveldict.get(level) + '漏洞，明天过期,请尽快处理或延期' + '\n' + '摘要：' + title.encode(
                                        "utf-8") + '\n' + '安全漏洞链接:' + url + str(step) + '?id=' + str(order_id) + '\n'
                            elif '16:00' > now > '12:00':
                                if create_time == today:
                                    msgp1 = '今日新增' + leveldict.get(level) + '漏洞，过期时间为:' + str(exptime) + '\n' + '摘要：' + title.encode("utf-8") + '\n' + '链接:' + url + str(step) + '?id=' + str(order_id) + '\n'
                                if exptime < today:
                                    msgp = '存在未修复' + leveldict.get(level) + '漏洞，已过期' + '\n' + '摘要：' + title.encode(
                                        "utf-8") + '\n' + '安全漏洞链接:' + url + str(step) + '?id=' + str(order_id) + '\n'
                            else:
                                msgp = '存在未修复' + leveldict.get(level) + '漏洞，过期时间为:' + str(
                                    exptime) + '\n' + '摘要：' + title.encode("utf-8") + '\n' + '安全漏洞链接:' + url + str(
                                    step) + '?id=' + str(order_id) + '\n'

                            #print msgp
                            msg = msg + msgp
                            msg1 = msg1 + msgp1
            msg = msg + msg1
            if msg:
                print msg
                print webhook
                xiaoding = DingtalkChatbot(webhook)
                xiaoding.send_text(msg, is_at_all=True)

    except Exception as e:
        yachurl = 'https://you.com/robot/send?access_token=OHpuw'
        yachsecret = 'SEC23f20a79e9'
        timestamp = long(round(time.time() * 1000))
        secret_enc = bytes(yachsecret).encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, yachsecret)
        string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.quote_plus(base64.b64encode(hmac_code))
        # print(timestamp)
        # print(sign)
        webhook = yachurl + "&timestamp=" + str(timestamp) + "&sign=" + sign
        xiaoding = DingtalkChatbot(webhook)

        xiaoding.send_text('yachrobot'+str(e) + '@13713', at_mobiles=['133'])




