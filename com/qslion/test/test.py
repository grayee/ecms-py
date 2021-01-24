import talib
import numpy
from wxpy import *

# print(numpy.array([1,2,3]))
#


import requests
import json


def send_dingding_msg(msg):
    access_token = '57318d7149e6fffa726ae86e9ef45fc3dbf2fd0a844def710b019faa98ba5465'
    # 钉钉生成的url
    url = 'https://oapi.dingtalk.com/robot/send?access_token=' + access_token
    # 中没有headers的'User-Agent'，通常会失败。
    headers = {"Content-Type": "application/json ;charset=utf-8 "}

    # 这里使用  文本类型，https://ding-doc.dingtalk.com/document/app/custom-robot-access/title-72m-8ag-pqw
    data = {
        "msgtype": "text",
        "text": {
            "content": "监控提醒：" + msg
        },
        "at": {
            "isAtAll": True
        }
    }

    try:
        r = requests.post(url, data=json.dumps(data).encode(encoding='utf-8'), headers=headers)
        print(r.text)
    except Exception as error:
        print('发送钉钉消息失败', error)


if __name__ == '__main__':
    send_dingding_msg("我就是我,是不一样的烟火")
