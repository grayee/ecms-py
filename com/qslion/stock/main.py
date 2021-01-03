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
    context.stock_today_open = {}
    # 最大交易资金比例
    context.ratio = 0.8
    # 标的池
    context.stocks = pd.DataFrame()
    # 缓存
    context.cached = True

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
    schedule(schedule_func=algo_trading, date_rule='1d', time_rule='09:30:00')
    # 每天的15:30 执行盘后策略algo_after_trading
    schedule(schedule_func=algo_after_trading, date_rule='1d', time_rule='15:30:00')

def algo_trading(context):
    last_stock = pd.DataFrame()
    if not context.stocks.empty:
        account_symbols = list(map(lambda x: x.symbol, context.account().positions()))
        cancel_sub_stocks = context.stocks[(~context.stocks['symbol'].isin(account_symbols)) & (
                context.now > context.stocks['eob'] + timedelta(4))]
        last_stock = context.stocks[(~context.stocks['symbol'].isin(cancel_sub_stocks['symbol']))]
        if not cancel_sub_stocks.empty:
            # 取消未持仓订阅，持仓订阅在卖出后取消
            unsubscribe(symbols=','.join(cancel_sub_stocks['symbol']), frequency='60s')
            unsubscribe(symbols=','.join(cancel_sub_stocks['symbol']), frequency='1d')
    # 过滤
    context.stocks = get_filter_stocks(context)
    if not context.stocks.empty:
        print('【'+context.now.strftime("%Y-%m-%d %H:%M:%S") + '】过滤结果：' + ','.join(context.stocks['symbol']))
        subscribe(symbols=','.join(context.stocks['symbol']), count=1, frequency='60s')
        subscribe(symbols=','.join(context.stocks['symbol']), count=1, frequency='1d')

    context.stocks = pd.concat([context.stocks, last_stock], ignore_index=True)

def algo_after_trading(context):
    context.stock_today_open = {}
    for stock in list(context.hold_days.keys()):
        # 持仓天数增加
        context.hold_days[stock] += 1

def on_bar(context, bars):
    if context.now.strftime("%Y-%m-%d %H:%M:%S") <= context.now.strftime("%Y-%m-%d") + " 15:00:00":
        # 在subscribe函数中订阅了多个标的的bar,同时wait_group参数值为true,返回包含多个标的的bars，否则每次返回只包含单个标的list长度为1的bars
        bar = bars[0]
        # subcribe_data = context.data(symbol=bar['symbol'], frequency='60s', count=15, fields='close')
        # close_mean_15m = subcribe_data['close'].mean()
        # print(bar['symbol']+':'+str(bar['close'])+'<======>'+str(close_mean_15m))
        # if bar['bob'].strftime("%Y-%m-%d %H:%M:%S") == context.now.strftime("%Y-%m-%d") + " 09:30:00":
        if context.stock_today_open.get(bar['symbol'], 0) == 0:
            context.stock_today_open[bar['symbol']] = bar['open']

        day_df = context.data(symbol=bar['symbol'], frequency='1d')
        today_open = context.stock_today_open.get(bar['symbol'], 0)

        # 上日day_df['eob'] < context.now
        pre_close = day_df.loc[0].close
        if day_df.loc[0].eob > context.now:
            pre_close = day_df.loc[0].pre_close


        # 1.买入策略：持仓数未达上限
        if not context.stocks.empty and len(context.account().positions()) < context.hold_max:
            stock_df = context.stocks[context.stocks['symbol'] == bar['symbol']]
            if not stock_df.empty:
                obj_stock = stock_df.iloc[0]
                if bar['close'] < obj_stock.ma5 * 1.02 and bar['close'] > obj_stock.low and not context.account().position(symbol=bar['symbol'], side=PositionSide_Long):
                    # 排除低开超过3%
                    if today_open > 0 and (today_open - pre_close) / pre_close > -0.03:
                        # 计算每个个股应该在持仓中的权重
                        percent = 1.0 / context.hold_max * context.ratio
                        # 限价买入
                        order_target_percent(symbol=bar['symbol'], percent=percent, order_type=OrderType_Limit,
                                             price=bar['close'], position_side=PositionSide_Long)
                        context.hold_days[bar['symbol']] = 0
                        print("标的：{},买入信号：{},买入限价：{},时间：{},持仓量:{}".format(bar['symbol'], obj_stock.ma5 * 1.02,
                                                                          bar['close'],
                                                                          bar['eob'].strftime("%Y-%m-%d %H:%M:%S"),
                                                                          len(context.account().positions())))

        # 2.卖出策略
        if len(context.account().positions()) > 0 and context.account().position(symbol=bar['symbol'],
                                                                                 side=PositionSide_Long):
            if context.hold_days.get(bar['symbol'], 0) >= 1:
                vwap = context.account().position(symbol=bar['symbol'], side=PositionSide_Long).vwap
                returns = 1.10
                if bar['symbol'].startswith('SZSE.300'):
                    returns = 1.15
                # 卖出策略1：预期收益+15%
                if bar['close'] / vwap > returns:
                    order_target_percent(symbol=bar['symbol'], percent=0, order_type=OrderType_Market,
                                         position_side=PositionSide_Long)

                    unsubscribe(symbols=bar['symbol'], frequency='60s')
                    unsubscribe(symbols=bar['symbol'], frequency='1d')
                    context.hold_days.pop(bar['symbol'])
                    rate = '{:.2f}%'.format((bar['close'] / vwap - 1) * 100)
                    print("标的：{},买出信号（{}）：{},持仓均价：{},时间：{},持仓量:{}".format(bar['symbol'],rate, bar['close'],
                                                                            vwap,
                                                                            bar['eob'].strftime("%Y-%m-%d %H:%M:%S"),
                                                                            len(context.account().positions())))

                # 卖出策略2：预期亏损-3%或者持股超过3天
                if bar['close'] / vwap < 0.97 or (pre_close > vwap and bar['close'] / pre_close < 0.97) or context.hold_days.get(bar['symbol'], 0) >= context.periods:
                    order_target_percent(symbol=bar['symbol'], percent=0, order_type=OrderType_Market,
                                         position_side=PositionSide_Long)
                    unsubscribe(symbols=bar['symbol'], frequency='60s')
                    unsubscribe(symbols=bar['symbol'], frequency='1d')
                    context.hold_days.pop(bar['symbol'])
                    rate = '{:.2f}%'.format((bar['close'] - vwap) * 100 / vwap)
                    print("标的：{},买出信号（{}）：{},持仓均价：{},时间：{},持仓量:{}".format(bar['symbol'], rate, bar['close'],
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
        history_n_data = history_n(symbol=row.symbol, frequency='1d', count=20, end_time=history_day,
                                   fields='symbol, pre_close,open, close, low, high, volume,amount,eob',
                                   adjust=ADJUST_PREV, df=True)

        ma20 = history_n_data['close'].mean()
        # 收盘价在5日均线之上
        ma5 = history_n_data.tail(5)['close'].mean()
        max_high5 = history_n_data['high'].max()
        if row.close > ma5:
            pre_row_df = history_n_data[-2:-1]
            if not pre_row_df.empty:
                pre_row = pre_row_df.iloc[0]
                # 前三個交易日去除漲停
                max3_limit_df = history_n_data[-4:-1].loc[lambda x: x.close / x.pre_close > 1.09]
                # 当日最低价小于等于上日最低价的80%，当日收盘价高于昨日最高价,最高价高于3日最高价，上一日涨幅或跌幅<9%,成交量大于流通盘10%
                if max3_limit_df.empty and row.low < pre_row.low * 1.02 and row.close > pre_row.high and row.high > max_high5 * 0.98 and \
                        abs((pre_row.close - pre_row.pre_close) / pre_row.close) < 0.09 and row.open < ma5 and row.low > ma20*0.98:
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
    # 振幅
    history_df['amplitude'] = history_df.apply(lambda x: (x.high - x.low) / x.low, axis=1).astype(float)
    history_df['pct_chg'] = history_df.apply(lambda x: (x.close - x.pre_close) / x.pre_close, axis=1).astype(float)
    # 过滤:振幅>8%,向下振幅>=%2,向上振幅大>=%2,涨幅>=%5
    history_df = history_df.loc[lambda x: (x.amplitude > 0.08) &  # 振幅>10%
                                          ((x.open - x.low) / x.low >= 0.02) &  # 向下振幅>=2%
                                          # ((x.high - x.close) / x.close > 0.02) &  # 向上振幅大>%2
                                          (x.pct_chg > 0.05) &  # 涨幅>=%5
                                          (x.close > x.pre_close)]  # 收盘高于昨日
    if not history_df.empty:
        fund_df = get_fundamentals(table='trading_derivative_indicator', symbols=','.join(history_df['symbol']),
                                   start_date=history_day, end_date=history_day,
                                   fields='NEGOTIABLEMV,TOTMKTCAP,TURNRATE,PELFY,PETTM,PEMRQ,PB,EVPS',
                                   df=True)

        # history_df['eob'] = history_df.apply(lambda x: x.eob.strftime("%Y-%m-%d"), axis=1)
        history_df = pd.merge(history_df, all_stock, how='left', on=['symbol'])
        history_df = pd.merge(history_df, fund_df, how='left', on=['symbol'])
        # 成交额大于流通盘的10%,換手率>10%
        history_df = history_df.loc[lambda x: (x.amount > x.NEGOTIABLEMV * 0.07) & (x.TURNRATE > 6)]
        ## 排序 ##
        history_df.sort_index(axis=1)
        history_df = history_df.sort_values(by=['amplitude'], ascending=False)
        # 重置索引
        history_df.reset_index(drop=True, inplace=True)
        # 改变数据列的顺序
        history_df = history_df[['eob', 'symbol', 'sec_name', 'pct_chg', 'amplitude', 'pre_close', 'close', 'open', 'high',
                                 'low', 'amount', 'volume','NEGOTIABLEMV','TOTMKTCAP','PETTM','PB','EVPS']]
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
        backtest_start_time='2020-12-01 09:30:00',
        backtest_end_time='2020-12-31 16:00:00',
        backtest_adjust=ADJUST_PREV,
        backtest_initial_cash=100000,
        backtest_commission_ratio=0.0001,
        backtest_slippage_ratio=0.0001)
