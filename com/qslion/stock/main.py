#!/usr/bin/python
# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
from datetime import timedelta
import pandas as pd
import sqlite3
"""
策略FlySky
"""
def init(context):
    # 1.设置策略参数
    # 最大持有股票数
    context.hold_max = 2
    # 持有天数
    context.periods = 3
    # 各股票持仓时间
    context.hold_days = {}
    # 最大交易资金比例
    context.ratio = 0.8
    # 标的池
    context.stocks = pd.DataFrame()
    # 缓存
    context.cached = False

    date1 = (context.now - timedelta(days=100)).strftime("%Y-%m-%d %H:%M:%S")
    date2 = context.now.strftime("%Y-%m-%d %H:%M:%S")
    # 通过get_instruments获取所有的上市股票代码
    all_stock = get_instruments(exchanges='SHSE, SZSE', sec_types=[1],
                                fields='symbol, sec_name,listed_date, delisted_date,sec_level', df=True)
    # 选取全A股（剔除停牌和st股和上市不足50日的新股和退市股和B股）
    context.all_stock = all_stock[(all_stock['listed_date'] < date1) & (all_stock['delisted_date'] > date2) &
                                  (all_stock['symbol'].str[5] != '9') & (all_stock['symbol'].str[5] != '2') &
                                  (all_stock['sec_level'] == 1) &
                                  (all_stock['symbol'].str.startswith('SZSE.300') | all_stock['symbol'].str.startswith(
                                      'SZSE.00') | all_stock['symbol'].str.startswith('SHSE.60'))]

    # 取消所有订阅
    unsubscribe(symbols='*', frequency='60s')
    # 每个交易日的09:45 定时执行algo任务
    schedule(schedule_func=algo_trading, date_rule='1d', time_rule='09:50:00')
    # 每天的15:30 执行盘后策略algo_after_trading
    schedule(schedule_func=algo_after_trading, date_rule='1d', time_rule='15:30:00')

def algo_trading(context):
    print("当前执行日期为：", context.now.strftime("%Y-%m-%d %H:%M:%S"))
    if not context.stocks.empty:
        account_symbols = list(map(lambda x: x.symbol, context.account().positions()))
        unsub_stocks = context.stocks[~context.stocks['symbol'].isin(account_symbols)]
        if not unsub_stocks.empty:
            # 取消未持仓订阅，持仓订阅在卖出后取消
            unsubscribe(symbols=','.join(unsub_stocks['symbol']), frequency='60s')
    # 过滤
    context.stocks = get_filter_stocks(context)
    if not context.stocks.empty:
        print('【'+context.now.strftime("%Y-%m-%d") + '】过滤结果：' + ','.join(context.stocks['symbol']))
        # data_df.to_csv('d:\\his-' + context.now.strftime("%Y-%m-%d") + '.csv', encoding='utf_8_sig')
        subscribe(symbols=','.join(context.stocks['symbol']), count=15, frequency='60s')

def algo_after_trading(context):
    for stock in list(context.hold_days.keys()):
        # 持仓天数增加
        context.hold_days[stock] += 1

def on_bar(context, bars):
    # 在subscribe函数中订阅了多个标的的bar,同时wait_group参数值为true,返回包含多个标的的bars，否则每次返回只包含单个标的list长度为1的bars
    bar = bars[0]
    subcribe_data = context.data(symbol=bar['symbol'], frequency='60s', count=15, fields='close')
    close_mean_15m = subcribe_data['close'].mean()
    # print(bar['symbol']+':'+str(bar['close'])+'<======>'+str(close_mean_15m))


    # 1.买入策略：持仓数未达上限
    if not context.stocks.empty and len(context.account().positions()) < context.hold_max:
        stock_df = context.stocks[context.stocks['symbol'] == bar['symbol']]
        if not stock_df.empty and bar['close'] < stock_df.iloc[0].ma5 * 1.02 and not context.account().position(
                symbol=bar['symbol'], side=PositionSide_Long):
            # 计算每个个股应该在持仓中的权重
            percent = 1.0 / context.hold_max * context.ratio
            # 限价买入
            order_target_percent(symbol=bar['symbol'], percent=percent, order_type=OrderType_Limit,
                                 price=bar['close'], position_side=PositionSide_Long)
            context.hold_days[bar['symbol']] = 0
            print("标的：{},买入信号：{},买入限价：{},时间：{},持仓量:{}".format(bar['symbol'], stock_df.iloc[0].ma5 * 1.02,
                                                              bar['close'],
                                                              bar['eob'].strftime("%Y-%m-%d %H:%M:%S"),
                                                              len(context.account().positions())))

    # 2.卖出策略
    if len(context.account().positions()) > 0 and context.account().position(symbol=bar['symbol'],
                                                                             side=PositionSide_Long):
        if context.hold_days.get(bar['symbol'], 0) >= 1:
            vwap = context.account().position(symbol=bar['symbol'], side=PositionSide_Long).vwap
            returns = 1.08
            if bar['symbol'].startswith('SZSE.300'):
                returns = 1.15

            # 卖出策略1：预期收益+15%
            if bar['close'] / vwap > returns:
                order_target_percent(symbol=bar['symbol'], percent=0, order_type=OrderType_Market,
                                     position_side=PositionSide_Long)

                unsubscribe(symbols=bar['symbol'], frequency='60s')
                context.hold_days.pop(bar['symbol'])
                print("标的：{},买出信号（+15%）：{},持仓均价：{},时间：{},持仓量:{}".format(bar['symbol'], bar['close'],
                                                                        vwap,
                                                                        bar['eob'].strftime("%Y-%m-%d %H:%M:%S"),
                                                                        len(context.account().positions())))

            # 卖出策略2：预期亏损-3%
            if bar['close'] / vwap < 0.97:  # or context.hold_days.get(bar['symbol'], 0) >= context.periods
                order_target_percent(symbol=bar['symbol'], percent=0, order_type=OrderType_Market,
                                     position_side=PositionSide_Long)
                unsubscribe(symbols=bar['symbol'], frequency='60s')
                context.hold_days.pop(bar['symbol'])
                print("标的：{},买出信号（-3%）：{},持仓均价：{},时间：{},持仓量:{}".format(bar['symbol'], bar['close'],
                                                                       vwap,
                                                                       bar['eob'].strftime("%Y-%m-%d %H:%M:%S"),
                                                                       len(context.account().positions())))



def get_filter_stocks(context):
    # 获取上一个交易日作为过滤日期条件
    history_day = get_previous_trading_date(exchange='SHSE', date=context.now)
    if context.cached:
        history_df = get_stock_history(context, history_day)
    else:
        history_df = get_stock_history(context, history_day)
        # with sqlite3.connect('history.db') as conn:
        #     history_df = pd.read_sql_query('SELECT h.* FROM his_raw h WHERE h.eob=%(his_day)s', conn,
        #                              params={'his_day': history_day})
        #     if history_df.empty:
        #         history_df = get_stock_history(context, history_day)

    data_df = pd.DataFrame()
    for row_index, row in history_df.iterrows():
        history_n_data = history_n(symbol=row.symbol, frequency='1d', count=5, end_time=history_day,
                                   fields='symbol, pre_close,open, close, low, high, volume,amount,eob',
                                   adjust=ADJUST_PREV, df=True)
        # 收盘价在5日均线之上
        ma5 = history_n_data['close'].mean()
        max_high5 = history_n_data['high'].max()
        if row.close > ma5:
            pre_row_df = history_n_data[-2:-1]
            if not pre_row_df.empty:
                pre_row = pre_row_df.iloc[0]
                # 当日最低价小于等于上日最低价的80%，当日收盘价高于昨日最高价,最高价高于3日最高价，上一日涨幅或跌幅<9%
                if row.low <= pre_row.low * 1.02 and row.close > pre_row.high and row.high > max_high5 * 0.98 and \
                        abs((pre_row.close - pre_row.pre_close) / pre_row.close) < 0.09:
                    row['ma5'] = ma5
                    row['plan_buy_price'] = ma5 * 1.02
                    row['plan_sell_price0'] = ma5 * 1.02 * 1.15
                    row['plan_sell_price1'] = ma5 * 1.02 * 0.97
                    data_df = data_df.append(row)

    if context.cached:
        cache_data(data_df, history_df)

    data_df.reset_index(drop=True, inplace=True)
    return data_df


def cache_data(data_df, history_df):
    with sqlite3.connect('history.db') as conn:
        dtype_dict = {
            'volume': 'INTEGER'
        }
        if not history_df.empty:
            history_df.to_sql('his_raw', conn, if_exists='append', index=False, dtype=dtype_dict)
        if not data_df.empty:
            data_df.to_sql('his_target', conn, if_exists='append', index=False, dtype=dtype_dict)


def get_stock_history(context, history_day):
    all_stock = context.all_stock
    history_df = history(symbol=','.join(all_stock['symbol']), frequency='1d', start_time=history_day,
                         end_time=history_day,
                         fields='symbol,pre_close,open, close, low, high, volume,amount,eob', adjust=ADJUST_PREV,
                         df=True)
    # 格式化为float，然后处理成%格式： {:.2f}%
    # history_df['amplitude'] = history_df.apply(lambda x: '{:.2f}%'.format((x.high - x.low)*100 / x.low), axis=1)
    # 振幅
    history_df['amplitude'] = history_df.apply(lambda x: (x.high - x.low) / x.low, axis=1).astype(float)
    # 过滤:振幅>8%,向下振幅>=5%,向上振幅大>%2,涨幅>=%5
    history_df = history_df.loc[lambda x: (x.amplitude >= 0.08) &  # 振幅>8%
                                          ((x.open - x.low) / x.low >= 0.03) &  # 向下振幅>=3%
                                          ((x.high - x.close) / x.close > 0.02) &  # 向上振幅大>%2
                                          ((x.close - x.pre_close) / x.pre_close >= 0.05) &  # 涨幅>=%5
                                          (x.close > x.pre_close)]  # 收盘高于昨日
    if not history_df.empty:
        history_df['stock_name'] = history_df.apply(
            lambda x: all_stock.loc[all_stock.symbol == x.symbol].iloc[0].sec_name,
            axis=1)
        ## 排序 ##
        history_df.sort_index(axis=1)
        history_df = history_df.sort_values(by=['amplitude'], ascending=False)
        # 重置索引
        history_df.reset_index(drop=True, inplace=True)
    return history_df


def on_backtest_finished(context, indicator):
    print('回测结束，绩效信息：', indicator)


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
        backtest_start_time='2020-12-15 09:30:00',
        backtest_end_time='2020-12-16 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=100000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)
