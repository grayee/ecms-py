# coding=utf-8
"""
    https://www.myquant.cn/docs/guide/672#101ce9e3d4683941
"""
from __future__ import print_function, absolute_import
from gm.api import *
import talib as tl


# 策略中必须有init方法，初始化函数
def init(context):
    # 每天14:50 定时执行algo任务,
    # algo执行定时任务函数，只能传context参数
    # date_rule执行频率，目前暂时支持1d、1w、1m，其中1w、1m仅用于回测，实时模式1d以上的频率，需要在algo判断日期
    # time_rule执行时间， 注意多个定时任务设置同一个时间点，前面的定时任务会被后面的覆盖
    schedule(schedule_func=algo, date_rule='1d', time_rule='14:50:00')
    subscribe(symbols='SZSE.300429', frequency='tick')
    # 1.设置策略参数
    # 最大持有股票数
    context.hold_max = 2
    # 持有天数
    context.periods = 3
    # 当前持仓数
    context.hold_count = 0
    # 各股票持仓时间
    context.hold_days = {}
    # 最大交易资金比例
    context.ratio = 0.8


# 调度，每日开盘执行###################################################################
def algo(context):
    print(context.now)
    # 通过get_instruments获取所有的上市股票代码
    all_stock = get_instruments(exchanges='SHSE, SZSE', sec_types=[1], fields='symbol, listed_date, delisted_date',
                                df=True)


#  数据事件是阻塞回调事件函数，通过subscribe函数订阅， 主动推送,接收固定周期bar数据
def on_tick(context, tick):
    print("tick:", tick)


def on_bar(context, bars):
    # 求均值 mean(context.data(symbols='SZSE.600000', frequency='60s'，fields =’close’))
    # 打印bar数据
    for bar in bars:
        print("bar:", bar)


def filter_stock():
    set_token('b526e92627f493aa90cdbae30a75407b63d1eae2')
    # 查询历史行情, 采用定点复权的方式， adjust指定前复权，adjust_end_time指定复权时间点
    data = history(symbol='SHSE.600000', frequency='1d', start_time='2020-12-07 09:30:00',
                   end_time='2020-12-07 16:00:00',
                   fields='open,high,low,close,amount,volume,bob,eob', adjust=ADJUST_PREV, adjust_end_time='2020-12-31',
                   df=True)


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
    run(strategy_id='95b02db3-3304-11eb-8b61-9c5a44904284',
        filename='mini_gold.py',
        mode=MODE_BACKTEST,
        token='b526e92627f493aa90cdbae30a75407b63d1eae2',
        backtest_start_time='2020-01-01 09:30:00',
        backtest_end_time='2020-12-07 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=100000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)

