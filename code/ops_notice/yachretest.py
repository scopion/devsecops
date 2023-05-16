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

app_id = '13903'
app_key = 'yNo0h'
session = requests.session()

#获取ticket
def getticket():
    data={"appid":app_id,"appkey":app_key}
    ticket_url = "http://al.com/basic/get_ticket"
    response = get(data,ticket_url)
    print (response)
    if response and response['errcode'] == 0:
        ticket = response['ticket']
    else:
        print ("获取ticket失败")
    return ticket

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
        'passwd': '0p0m',
        'db': 'ops',
        'charset': 'utf8',
        'cursorclass': MySQLdb.cursors.DictCursor
    }
    conn = mdb.connect(**config)
    return conn

def getorder(conn):
    dictorder = {}
    sql = 'select order_id,create_uid  from ops_order where step=3'
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchall()
    #print results.__class__
    for p in results:
        order_id = p.get('order_id')
        create_uid = p.get('create_uid')
        #print id.__class__
        #print group
        dictorder['order_id'] = order_id
        dictorder['create_uid'] = create_uid
        print dictorder
    print 'get dict success'
    # except:
    #     # Rollback in case there is any error
    #     print 'select dict fail,rollback'
    return results


def getphone(conn,id):
    phone=''
    sql = 'select mobile from ops_user where id=' + id
    print sql
    cursor = conn.cursor()
    # try:
        #print 'get status start'
        # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    results = cursor.fetchall()
    #print results.__class__
    for p in results:
        phone = p.get('mobile')
        print phone
    print 'get dict success'
    # except:
    #     # Rollback in case there is any error
    #     print 'select dict fail,rollback'
    return phone



if __name__ == '__main__':
    try:

        yachurl = 'https://yacou.com/robot/send?access_token=bUVE9WNA'
        yachsecret = 'SECe17694c61b123'
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


        # 初始化机器人小丁
        url = 'http://oom/admin/order/step3'
        conn = getmysqlconn()
        orderdict = getorder(conn)
        msg = '发现重新检测漏洞，地址为:\n'
        phoneset = set()
        if orderdict:
            for i in orderdict:
                print i
                print i.__class__
                id = i.get('order_id')
                uid = i.get('create_uid')
                phonenum = getphone(conn, str(uid))
                print phonenum
                phoneset.add(phonenum)
                msgp = url + '?id=' + str(id) + '\n'
                print msgp
                msg = msg + msgp
            # mobiles = eval(phoneset)
            at_phone = '@'+'@'.join(phoneset)
            xiaoding.send_text(msg+at_phone.encode('utf-8'), at_mobiles=phoneset)

    except Exception as e:
        yachurl = 'https://yacou.com/robot/send?access_token=OHpucEZcUNIKw'
        yachsecret = 'SEC23f120a79e9'
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

        xiaoding.send_text('yachretest'+str(e) + '@13773', at_mobiles=['137'])




