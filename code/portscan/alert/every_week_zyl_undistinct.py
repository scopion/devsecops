#! /usr/bin/env python
# _*_ coding:utf-8 _*_

import json
import datetime
from datetime import timedelta
import requests
import MySQLdb.cursors
import MySQLdb as mdb
import time
import logging
import requests
import plotly
import plotly.offline as py
import plotly.graph_objs as go
from plotly.offline import plot
import plotly.io as pio
import hmac
import hashlib
import base64
import urllib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# 以下为钉钉消息类及方法
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

    def __init__(self, webhook,secret):
        """
        机器人初始化
        :param webhook: 钉钉群自定义机器人webhook地址
        """
        super(DingtalkChatbot, self).__init__()
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.times = 0
        self.start_time = time.time()
        timestamp = long(round(time.time() * 1000))
        secret = secret
        secret_enc = bytes(secret).encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = bytes(string_to_sign).encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.quote_plus(base64.b64encode(hmac_code))
        print(timestamp)
        print(sign)
        self.webhook = webhook + "&timestamp=" + str(timestamp) + "&sign=" + sign

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

            print "data=",data
            logging.debug("markdown类型：%s" % data)
            return self.post(data)
        else:
            logging.error("markdown类型中消息标题或内容不能为空！")
            raise ValueError("markdown类型中消息标题或内容不能为空！")

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
            response = requests.post(self.webhook, headers=self.headers, data=post_data)
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
                    error_data = {"msgtype": "text", "text": {"content": "知音楼机器人消息发送失败，原因：%s" % result['msg']},
                                  "at": {"isAtAll": True}}
                    logging.error("消息发送失败，自动通知：%s" % error_data)
                    requests.post(self.webhook, headers=self.headers, data=json.dumps(error_data))
                return result

now_time = datetime.datetime.now()
this_week_start = now_time - timedelta(days=now_time.weekday())
this_week_start_all = this_week_start.strftime('%Y-%m-%d')
this_week_start_port = this_week_start.strftime('%Y-%m-%d 00:00:00')
print "this_week_start_port=", this_week_start_port
this_week_end = now_time + timedelta(days=4 - now_time.weekday())
this_week_end_all = this_week_end.strftime('%Y-%m-%d')
this_week_end_port = this_week_end.strftime('%Y-%m-%d 23:00:00')
print "this_week_end_port=", this_week_end_port
time_unix = int(time.time())
print "time_unix=",time_unix


#正式数据库
def getmysqlconn():
    config = {
        'host': '*.*.*.*',#127.0.0.1
        'port': **,
        'user': '**',
        'passwd': '****',
        'db': '**',
        'charset': 'utf8',
        'cursorclass': MySQLdb.cursors.DictCursor
    }
    conn = mdb.connect(**config)
    return conn


#清空数据库表everyday_find数据
def truncate(conn):
    cursor = conn.cursor()
    # SQL update sql
    sql = "truncate table everyday_findport"
    try:
        # 执行sql语句
        n = cursor.execute(sql)
        # 提交到数据库执行
        conn.commit()
        print 'clear success.'
    except:
        # Rollback in case there is any error
        conn.rollback()
        print 'clear  fail,rollback.'

#查询每周敏感端口的数据
def sel_pp(conn):
    first = this_week_start_port
    end = this_week_end_port
    #first = "2020-07-27 00:00:00"
    #end = "2020-07-31 23:00:00"
    cursor = conn.cursor()
    #sql_pp = "SELECT bline,cdate,ip,`port` from oms_portscan where cdate BETWEEN '" + first + "' AND '" + end + "'"
    sql_pp = "select bline,oms_portscan.`ip`, `port`,service,yachurl,yachsecret,oms_portscan.cdate from oms_portscan,authorization_group where oms_portscan.group_id=authorization_group.`id` and cdate BETWEEN %s  AND %s"
    try:
        val_p = (first, end)
        # 执行sql语句
        n = cursor.execute(sql_pp,val_p)
        # 提交到数据库执行
        res_pp = cursor.fetchall()
        print "select port count sucess."
    except Exception, err:
        print ("Exception:", err)
        print "select port count fail."
    #print "results_pp=", res_pp
    for pp in res_pp:
        bline = pp.get('bline').encode('utf-8')
        bline = bline.split('-')[-1]
        #print "bline=",bline
        cdate = pp.get('cdate')
        cdate = cdate.strftime('%Y-%m-%d')
        ip = pp.get('ip').encode('utf-8')
        port = pp.get('port')
        service = pp.get('service').encode('utf-8')
        address = pp.get('yachurl').encode('utf-8')
        yachsecret = pp.get('yachsecret').encode('utf-8')
        #phone = pp.get('phone').encode('utf-8')
        insert_week(bline, cdate, ip, port, service, address, yachsecret)

#插入数据
def insert_week(bline,cdate,ip,port,service,address,yachsecret):
    curs = conn.cursor()
    sql ="insert into everyday_findport(bline,cdate,ip,port,service,address,yachsecret) values(%s,%s,%s,%s,%s,%s,%s)"
    values = (bline,cdate,ip,port,service,address,yachsecret)
    try:
        res = curs.execute(sql, values)
        conn.commit()
        print 'insert every_week success.'
    except Exception, e:
        print e
        conn.rollback()
        print 'insert every_week fail,rollback.'

#绘制柱状图和折线图
def bar_chart(conn):
    first = this_week_start_all
    end = this_week_end_all
    print "bar_first=",first
    #first = "2020-07-27"
    #end = "2020-07-31"
    curs = conn.cursor()
    # 分组去重，统计(ip＋port+bline)的组合唯一值
    # sql_bar = "SELECT bline,COUNT(*) as count from (SELECT DISTINCT ip,`port`,bline from everyday_find where cdate BETWEEN '" + first + "' AND '" + end + "')A  GROUP BY bline HAVING count>=1 order by count desc"
    sql_bar = "SELECT bline,COUNT(*) as count from (SELECT ip,`port`,bline from everyday_findport where cdate BETWEEN %s AND %s)A  GROUP BY bline HAVING count>=1 order by count desc"
    try:
        val_bar = (first,end)
        # 执行sql语句
        n = curs.execute(sql_bar,val_bar)
        # 提交到数据库执行
        res_week = curs.fetchall()
        print "select week sucess."
    except Exception, err:
        print ("Exception:", err)
        print "select week fail."
    print "res_week=", res_week
    lists = [[], []]
    for row in res_week:
        bline = row.get('bline').encode('utf-8')
        num = row.get('count')
        print "num=", num
        lists[0].append(bline)
        lists[1].append(num)

        #折线图
        sql_zx = "SELECT cdate,COUNT(*) as count from everyday_findport where  bline=%s and cdate BETWEEN %s AND %s GROUP BY cdate "
        print "sql=", sql_zx
        try:
            val_zx = (bline,first, end)
            # 执行sql语句
            n = curs.execute(sql_zx,val_zx)
            # 提交到数据库执行
            zhexian_date = curs.fetchall()
            print "select sucess."
        except Exception, err:
            print ("Exception:", err)
        print "rzhexian_date=", len(zhexian_date)

        # 获取当前周的周一至周五的日期列表
        dates = []
        print "this_week_start=", this_week_start
        dt = datetime.datetime.strptime(this_week_start_all, "%Y-%m-%d")
        print "dt=",dt
        date = this_week_start_all[:]
        while date <= this_week_end_all:
            dates.append(date)
            dt = dt + datetime.timedelta(1)
            date = dt.strftime("%Y-%m-%d")
        print "dates=", dates
        date_lists = [dates, [0, 0, 0, 0, 0]]
        lists_zx = [[], []]
        if len(zhexian_date) >= 1:
            for row in zhexian_date:
                cdate = row.get('cdate').encode('utf-8')
                num = row.get('count')
                lists_zx[0].append(cdate)
                lists_zx[1].append(num)

            print "lists_zx[0]=", lists_zx[0]
            print "lists_zx[1]=", lists_zx[1]

            for i in range(len(lists_zx[0])):
                # 从列表中找出某个值第一个匹配项的索引位置
                j = dates.index(lists_zx[0][i])
                print "j=", j
                date_lists[1][j] = lists_zx[1][i]
                # print date_lists[1][j]
            x = date_lists[0]
            y = date_lists[1]
            print "x=", x
            print "y=", y

            # 折线图,family：str型，用于控制字体，默认为'Open Sans'，可选项有'verdana'，'arial'，'sans-serif'等等
            trace1 = go.Scatter(x=x, y=y, mode='lines+text', name=u"num", text=y, textposition="top center",
                                textfont=dict(color='red'))
            layout = go.Layout(title=dict(text=bline + u"本周敏感服务开放情况", font=dict(family='sans-serif',size=20, color='#392f41'), x=0.5),
                               showlegend=True, legend=dict(x=0.9, y=1.1),
                               yaxis=dict(zeroline=True, autorange=False, range=[0.0, max(y) + 2], dtick=1),
                               xaxis=dict(tickformat='%Y-%m-%d'))
            figure = go.Figure(data=[trace1], layout=layout)
            # 设置为离线模式
            # plotly.offline.init_notebook_mode(connected=True)
            print "time_unix=", str(time_unix)[0:8]
            if bline == "？？":

            else:
                fb_name = bline + str(time_unix)[0:8] + ".png"
                file_html_zxn = bline + str(time_unix)[0:8] + ".html"
                file_html_zx = "/opt/aliyunavds/image/every_week/" + file_html_zxn
            print "fb_name=",fb_name
            output_png_zx = "/opt/aliyunavds/image/every_week/July/" + fb_name
            pio.write_image(figure, output_png_zx)
            # 生成html
            plotly.offline.plot(figure, filename=file_html_zx)


    #柱状图
    x = lists[0]
    y = lists[1]
    if len(x) >=1:
        date_bline = go.Bar(x=x,y=y,text=y,textposition = 'outside',name = "total",textfont=dict(family='sans-serif'))
        date = [date_bline]
        #barmode=[stack, group, overlay, relative]，设置相同坐标的条形图位置。包括 : stack(叠加)、group(并列)、overlay(覆盖)、relative(相对)；
        layout = go.Layout(title=dict(text=u"本周敏感服务开放情况统计", font=dict(family='sans-serif',size=20, color='#392f41'),x=0.5),yaxis=dict(zeroline=True, autorange=False, range=[0.0, max(y) + 5], dtick=5),legend=dict(x=0.9,y=1.1),showlegend=True,paper_bgcolor='#D3D3D3',margin=go.Margin(l=15,r=15))
        fig = go.Figure(data=date, layout=layout)
        # 设置为离线模式
        # plotly.offline.init_notebook_mode(connected=True)
        print "time_unix=", str(time_unix)
        file_name = str(time_unix) + end + ".png"
        print "file_name=",file_name
        output_png = "/opt/aliyunavds/image/every_week/July/" + file_name
        pio.write_image(fig, output_png)
        #html
        file_html_zzn = str(time_unix) + end + ".html"
        file_html_zz = "/opt/aliyunavds/image/every_week/"+ file_html_zzn
        plotly.offline.plot(fig, filename= file_html_zz)

        for i in range(len(x)):
            bline = x[i]
            print "bline=",bline
            if bline == "？？？":
            else:
                fb_name = bline + str(time_unix)[0:8] + ".png"
            print "fb_name=",fb_name
            # send_ding(conn, bline ,file_name,fb_name,file_html_zzn,file_html_zxn)

    else:
        sys.exit(0)


#发送消息
def send_ding(conn,bline,file_name,fb_name,file_html_zzn,file_html_zxn):
    cursor = conn.cursor()
    print "bline=", bline
    sql_address = "select bline,address,yachsecret from everyday_findport where bline=%s GROUP BY bline,address,yachsecret"
    vul = (bline,)
    try:
        # 执行sql语句
        n = cursor.execute(sql_address,vul)
        # 提交到数据库执行
        res_address = cursor.fetchall()
        print "select address sucess."
    except Exception, err:
        print ("Exception:", err)
        print "select address fail."
    print "res_address=", res_address
    for m in res_address:
        address = m.get('address').encode("utf-8")
        print "webhook=", address
        secret = m.get('yachsecret').encode("utf-8")
        # 初始化机器人小丁
        xiaoding = DingtalkChatbot(address, secret)
        print "开始发送消息"
        title = "本周敏感服务开放情况"
        text = "### **本周敏感服务开放情况:** \n" + "![screenshot](https://com/image/every_week/July/" + file_name + ")\n" + "##### [查看柱状图原图](https://bcom/image/every_week/" + file_html_zzn + ") \n"+ "![screenshot](https://b.com/image/every_week/July/" + fb_name + ")\n" + "##### " + this_week_start_all + "至" + this_week_end_all + " [查看折线图原图](https://b.com/image/every_week/" + file_html_zxn + ") \n"+ "\n"
        xiaoding.send_markdown(title, text)
        print "发送消息成功"

if __name__ == '__main__':
    conn = getmysqlconn()
    truncate(conn)
    sel_pp(conn)
    bar_chart(conn)
    conn.close()
