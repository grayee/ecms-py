# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from datetime import timedelta
import pandas as pd

"""
小市值策略
本策略每个月触发一次，计算当前沪深市场上市值最小的前30只股票，并且等权重方式进行买入。
对于不在前30的有持仓的股票直接平仓。
回测时间为：2018-07-01 08:00:00 到 2019-10-01 16:00:00 
"""


def init(context):
    # schedule 定时任务详见： https://www.myquant.cn/docs/python/python_basic#7bce6621a1abafe8
    # 每月第一个交易日的09:40 定时执行algo任务
    schedule(schedule_func=algo, date_rule='1d', time_rule='09:40:00')

    # 使用多少的资金来进行开仓。
    context.ratio = 0.8


def algo(context):
    # 获取当前时间
    now = context.now
    # 获取上一个交易日
    last_day = get_previous_trading_date(exchange='SHSE', date=now)
    print("上一个交易日:", last_day)
    data_df = get_filter_stocks(context, last_day)
    print(data_df)





# code.to_csv('d:\\code.csv')

# 通过get_instruments获取所有的上市股票代码 详见：https://www.myquant.cn/docs/python/python_select_api#8ba2064987fb1d1f
# code = get_instruments(exchanges=['SHSE', 'SZSE'], sec_types=SEC_TYPE_STOCK, df=True)

# 获取所有股票在这个时候的市值， 详见： https://www.myquant.cn/docs/python/python_select_api#8ba2064987fb1d1f
# fundamental = get_fundamentals_n('trading_derivative_indicator', code['symbol'].to_list(),
#                                  context.now, fields='TOTMKTCAP', order_by='TOTMKTCAP', count=1, df=True)

# 去掉数据中包含‘SHSE.900’ 和 ‘SZSE.200’的股票，即B股。
# fundamental = fundamental.loc[~fundamental['symbol'].str.contains('SHSE.900'), :]
# fundamental = fundamental.loc[~fundamental['symbol'].str.contains('SZSE.200'), :]

# 对市值进行排序，并且获取前30个。 最后将这个series 转化成为一个list即为标的池
# trade_symbols = fundamental.reset_index(drop=True).loc[:29, 'symbol'].to_list()

# print('本次股票池有股票数目: ', len(trade_symbols))

# # 计算每个个股应该在持仓中的权重
# percent = 1.0 / len(trade_symbols) * context.ratio
#
# # 获取当前所有仓位 详见 https://www.myquant.cn/docs/python/python_concept#8079e2e4dad05879
# positions = context.account().positions()
#
# # 平不在标的池的仓位
# for position in positions:
#     symbol = position['symbol']
#     if symbol not in trade_symbols:
#         order_target_percent(symbol=symbol, percent=0, order_type=OrderType_Market,
#                              position_side=PositionSide_Long)
#         print('市价单平不在标的池的', symbol)
#
# # 将标中已有持仓的和还没有持仓的都调整到计算出来的比例。
# for symbol in trade_symbols:
#     order_target_percent(symbol=symbol, percent=percent, order_type=OrderType_Market,
#                          position_side=PositionSide_Long)
#     print(symbol, '以市价单调整至权重', percent)


def  get_filter_stocks(context, history_day):
    # 选取全A股（剔除停牌和st股和上市不足50日的新股和退市股和B股）
    date1 = (context.now - timedelta(days=100)).strftime("%Y-%m-%d %H:%M:%S")
    date2 = context.now.strftime("%Y-%m-%d %H:%M:%S")
    # 通过get_instruments获取所有的上市股票代码 详见：https://www.myquant.cn/docs/python/python_select_api#8ba2064987fb1d1f
    all_stock = get_instruments(exchanges='SHSE, SZSE', sec_types=[1],
                                fields='symbol, sec_name,listed_date, delisted_date',
                                df=True)
    code_df = all_stock[(all_stock['listed_date'] < date1) & (all_stock['delisted_date'] > date2) &
                        (all_stock['symbol'].str[5] != '9') & (all_stock['symbol'].str[5] != '2')]
    history_df = history(symbol=','.join(code_df['symbol']), frequency='1d', start_time=history_day,
                         end_time=history_day,
                         fields='symbol,pre_close,open, close, low, high, volume,amount,eob,bob', adjust=ADJUST_PREV,
                         df=True)
    # history_n_data = history_n(symbol='SZSE.002519', frequency='1d', count=13, end_time=now,
    #                            fields='symbol, open, close, low, high, eob', adjust=ADJUST_PREV, df=True)
    # 格式化为float，然后处理成%格式： {:.2f}%
    # history_df['amplitude'] = history_df.apply(lambda x: '{:.2f}%'.format((x.high - x.low)*100 / x.low), axis=1)
    # 振幅
    history_df['amplitude'] = history_df.apply(lambda x: round((x.high - x.low) / x.low, 2), axis=1).astype(float)

    # 过滤:振幅>8%,向下振幅>=5%,向上振幅大>%2,涨幅>=%5
    history_df = history_df.loc[lambda x: (x.amplitude >= 0.08) & ((x.close - x.low) / x.low >= 0.05) & (
            (x.high - x.close) / x.close > 0.02) & (x.close > x.pre_close)]

    ##排序##
    history_df.sort_index(axis=1)
    history_df = history_df.sort_values(by=['amplitude'], ascending=False)
    # 重置索引
    history_df.reset_index(drop=True, inplace=True)
    history_df.to_csv('d:\\his.csv')

    # 前日
    before_day = get_previous_trading_date(exchange='SHSE', date=history_day)
    print("前日", before_day)

    pre_his_df = history(symbol=','.join(history_df['symbol']), frequency='1d', start_time=before_day,
                         end_time=before_day,
                         fields='symbol,pre_close,open, close, low, high, volume,amount,eob,bob', adjust=ADJUST_PREV,
                         df=True)

    data_df = pd.DataFrame()
    for row_index, row in history_df.iterrows():
        pre_row = pre_his_df[pre_his_df.symbol == row.symbol]
        # print("pre===>>",pre_row)
        print("cur===>>", row)
        # 当日最低价小于等于上日最低价，当日收盘价高于上日最高价,上一日涨幅或跌幅<10%
        # if row.low <= pre_row.low and row.close > pre_row.high and abs(pre_row.close - pre_row.open) < 10:
        #     data_df.append(row)

    return data_df


if __name__ == '__main__':
    '''
    strategy_id策略ID,由系统生成
    filename文件名,请与本文件名保持一致
    mode实时模式:MODE_LIVE回测模式:MODE_BACKTEST
    token绑定计算机的ID,可在系统设置-密钥管理中生成
    backtest_start_time回测开始时间
    backtest_end_time回测结束时间
    backtest_adjust股票复权方式不复权:ADJUST_NONE前复权:ADJUST_PREV后复权:ADJUST_POST
    backtest_initial_cash回测初始资金
    backtest_commission_ratio回测佣金比例
    backtest_slippage_ratio回测滑点比例
    '''
    run(strategy_id='c477468b-882a-11ea-b2b5-0a0027000006',
        filename='main.py',
        mode=MODE_BACKTEST,
        token='b526e92627f493aa90cdbae30a75407b63d1eae2',
        backtest_start_time='2020-12-08 08:00:00',
        backtest_end_time='2020-12-08 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=1000000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)
