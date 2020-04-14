# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:25:02 2020

@author: Administrator
"""

import requests
import cx_Oracle

## 1.1 服务器地址检查
response = requests.get('http://172.16.8.120/maimai/pages/main/home-page.jsp')
print(response.status_code== requests.codes.ok)
response = requests.get('https://maimai.maitian.cn/maimai/app.do?method=getQr')
print(response.status_code== requests.codes.ok)
## 1.2 图片地址的检查
response = requests.get('https://mmdown.maitian.cn/default/maimai512.png')
print(response.status_code== requests.codes.ok)
## 1.3.检查租赁刷新缓存和ES的中间表
conn = cx_Oracle.connect('BSS_MAIMAI_BEIJING/N2QxMWQ4NjIxOWI3@172.16.6.118:1521/phydb')
print("数据库连接成功：", conn)
#打开语句要使用的游标
cur = conn.cursor()
#分析并执行语句
cur.execute('select count(1) from rh_data_change_record t where t.status = 0')
row = cur.fetchone()
print("租赁刷新缓存和ES的中间表结果（0是正常不为0多刷新几次）：",row)

## 1.4.	检查HR同步的中间表
cur.execute('select count(1) from org_sync_data t where t.status = 0')
row = cur.fetchone()
print("HR同步的中间表结果：",row)

## 1.9.检查消息记录表中的数据
cur.execute('select count(1) from msg_business_record t where t.state = 0')
row = cur.fetchone()
print("消息记录表中的数据（正常为0）：",row)
## 1.10.检查消息记录发送表中的数据
cur.execute('select count(1) from msg_business_record_send t where t.state = 0')
row = cur.fetchone()
print("消息记录发送表中的数据（正常为0）：",row)


##1.17.	租赁房源到期提醒
cur.execute("select count(*) from msg_business_record t where t.code in ('RH0008', 'RH0007') and t.create_time > sysdate - 1")
row = cur.fetchone()
cur.execute("select count(1) from renthouse_info_tbl t where ((t.sign_endtime between to_date(to_char(sysdate, 'yyyy/mm/dd'), 'yyyy/mm/dd') + 3 and to_date(to_char(sysdate, 'yyyy/mm/dd') || ' 23:59:59','yyyy/mm/dd hh24:mi:ss') + 3) or (t.sign_endtime between to_date(to_char(sysdate, 'yyyy/mm/dd'), 'yyyy/mm/dd') + 30 and to_date(to_char(sysdate, 'yyyy/mm/dd') || ' 23:59:59','yyyy/mm/dd hh24:mi:ss') + 30))")
row1 = cur.fetchone()
print("租赁房源到期提醒：",row==row1)


##1.23.	新房数据检查HR同步的中间表
cur.execute('select count(1) from bss_newhouse_beijing.sys_sync_data t where t.status=0')
row = cur.fetchone()
print("新房数据检查HR同步的中间表（正常为0）：",row)

cur.close()
conn.close()

##1.22.	检查KAFKA同步麦脉是否正常
response = requests.post('http://172.16.8.133/msgQueueProducerServer/linkStatus?topicName=beijinghr')
print("检查KAFKA同步麦脉是否正常:",response.text)

