# coding=utf-8
"""
    https://www.myquant.cn/docs/guide/672#101ce9e3d4683941
"""
from __future__ import print_function, absolute_import
from gm.api import *
from easytrader import grid_strategies
import easytrader
import requests
import json
import pandas as pd

# 策略中必须有init方法，初始化函数
def init(context):
    # 每天14:50 定时执行algo任务,
    # algo执行定时任务函数，只能传context参数
    # date_rule执行频率，目前暂时支持1d、1w、1m，其中1w、1m仅用于回测，实时模式1d以上的频率，需要在algo判断日期
    # time_rule执行时间， 注意多个定时任务设置同一个时间点，前面的定时任务会被后面的覆盖
    # schedule(schedule_func=algo, date_rule='1d', time_rule='14:50:00')
    # subscribe(symbols='SHSE.600478', frequency='30s')
    subscribe(symbols='SHSE.600000', frequency='1d',count=3)
    subscribe(symbols='SHSE.600360', frequency='60s')



# 调度，每日开盘执行###################################################################
def algo(context):
    print(context.now)



#  数据事件是阻塞回调事件函数，通过subscribe函数订阅， 主动推送,接收固定周期bar数据
def on_tick(context, tick):
    print("tick:", tick)


def on_bar(context, bars):
    # 求均值 mean(context.data(symbols='SZSE.600000', frequency='60s'，fields =’close’))
    Subcribe_data = context.data(symbol='SHSE.600000', frequency='1d', count=3, fields='symbol,open,close,volume,eob')
    # 打印bar数据
    print("bar:", bars)


def test_eastMoney():
    data = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38", "pageNo": 1, "pageSize": 100}
    headers = {'content-type': 'application/json'}
    ##人气榜
    rk_rs = requests.post('https://emappdata.eastmoney.com/stockrank/getAllCurrentList', data=json.dumps(data),
                          headers=headers)
    rk_df = pd.DataFrame(json.loads(rk_rs.text).get('data'))
    print(rk_df)
    # 人气飙升榜
    crk_rs = requests.post('https://emappdata.eastmoney.com/stockrank/getAllHisRcList', data=json.dumps(data),
                           headers=headers)
    crk_df = pd.DataFrame(json.loads(crk_rs.text).get('data'))
    print(crk_df)
    # 热点原因
    rs = requests.get(url='https://vipmoney.eastmoney.com/collectapi/ranking/GubaHotTopicNew',
                      params={'code': '000591'})
    print(json.loads(rs.text).get('re'))
    # 实时排名
    stock_data = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38", "srcSecurityCode": 'SH601608'}
    sk_rs = requests.post('https://emappdata.eastmoney.com/stockrank/getCurrentList', data=json.dumps(stock_data),
                          headers=headers)
    print(pd.DataFrame(json.loads(sk_rs.text).get('data')))


if __name__ == '__main__':
    '''
        strategy_id策略ID, 由系统生成
        filename文件名, 请与本文件名保持一致
        mode运行模式, 实时模式:MODE_LIVE回测模式:MODE_BACKTEST
        token绑定计算机的ID, 可在系统设置-密钥管理中生成
        backtest_start_time回测开始时间
        backtest_end_time回测结束时间
        backtest_adjust股票复权方式, 不复权:ADJUST_NONE前复权:ADJUST_PREV后复权:ADJUST_POST
        backtest_initial_cash回测初始资金
        backtest_commission_ratio回测佣金比例
        backtest_slippage_ratio回测滑点比例
    '''
    # run(strategy_id='95b02db3-3304-11eb-8b61-9c5a44904284',
    #     filename='mini_gold.py',
    #     mode=MODE_LIVE,
    #     token='b526e92627f493aa90cdbae30a75407b63d1eae2',
    #     backtest_adjust=ADJUST_PREV,
    #     backtest_initial_cash=100000,
    #     backtest_commission_ratio=0.0001,
    #     backtest_slippage_ratio=0.0001)

    # run(strategy_id='c477468b-882a-11ea-b2b5-0a0027000006',
    #     filename='mini_gold.py',
    #     mode=MODE_BACKTEST,
    #     token='b526e92627f493aa90cdbae30a75407b63d1eae2',
    #     backtest_start_time='2020-12-15 09:30:00',
    #     backtest_end_time='2020-12-17 16:00:00',
    #     backtest_adjust=ADJUST_PREV,
    #     backtest_initial_cash=100000,
    #     backtest_commission_ratio=0.0001,
    #     backtest_slippage_ratio=0.0001)

    # user = easytrader.use('gj_client')
    # user.prepare(user='39271642', password='523120', comm_password='')
    #
    user = easytrader.use('ths')
    user.grid_strategy = grid_strategies.Xls
    user.connect(r'E:\Program\同花顺远航版\transaction\xiadan.exe')  # 类似 r'C:\htzqzyb2\xiadan.exe'
    positions = user.position
    balance = user.balance
    print(balance)
    print(positions)
    user.buy('300335', price=5.5, amount=100)


