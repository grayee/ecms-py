import talib
import numpy
from wxpy import *

# print(numpy.array([1,2,3]))
#


import requests
import json


def get_access_token():
    """
    获取微信全局接口的凭证(默认有效期俩个小时)
    如果不每天请求次数过多, 通过设置缓存即可
    """
    result = requests.get(
        url="https://api.weixin.qq.com/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": "wx7466a840388f72eb",
            "secret": "103cde8efc413d482eedf182f5c1d891",
        }
    ).json()

    if result.get("access_token"):
        access_token = result.get('access_token')
    else:
        access_token = None
    return access_token


def sendmsg(openid, msg):
    access_token = get_access_token()

    body = {
        "touser": openid,
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }
    response = requests.post(
        url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
        params={
            'access_token': access_token
        },
        data=bytes(json.dumps(body, ensure_ascii=False), encoding='utf-8')
    )
    # 这里可根据回执code进行判定是否发送成功(也可以根据code根据错误信息)
    result = response.json()
    print(result)


if __name__ == '__main__':
    sendmsg('qslion', '发送消息内容')
