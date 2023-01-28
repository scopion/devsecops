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

app_id = '13603'
app_key = 'yNo0h'

session = requests.session()

def list_split(items, n):
    return [items[i:i+n] for i in range(0, len(items), n)]



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
    ticket_url = "http://aal.com/basic/get_ticket"
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
                print(users)
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




    empl_ids = ['064406','133239']
    noticelist = list_split(empl_ids, 90)
    title="青藤云安装提醒"
    text="老师，您好：\n  \n 后台检测到您的部门还有老师的个人开发机未安装青藤安全软件。\
        近日，安全中台排查的网校发生多起服务器入侵事件，皆由个人开发机配置或服务不当等问题引发。此类服务器潜在威胁很大。\
        请您督促组员尽快于2020年12月30日前安装青藤软件。安全中台会尽快排查威胁，赋能业务发展。\n\
         [课程学习请使用ctrl+c将该链接复制到浏览器地址栏进行访问]\n " \
         "http://tg.cn/kng/view/package/b497bdaedce34a55b59ee8d17d24db72.html \n " \
         "本通知非学堂发送，直接点击将无法访问。 温馨提示：考试通过才算学习完成，在学习和考试的过程中存在疑问可通过0获得反馈。"
    for i in noticelist:
        print (i)
        response =xiaoding.send_yach_markdown(ticket,title,text,user_type='workcode',at_users=i)
        print (response)







