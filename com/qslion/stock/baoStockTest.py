# -*- coding: utf-8 -*-

import baostock as bs
import pandas as pd
import datetime



def download_data(date):
    # data_df = download_data_by_day(date)
    # data_df = filter_data(data_df)

    datetime.date.today() + datetime.timedelta(1)

    print(datetime.datetime.strptime(date, "%Y-%m-%d"))
    print(datetime.date.today())
    # 输出
    # print(data_df)
    # data_df.to_csv("D:\\demo_assignDayData.csv", encoding="gbk", index=False)


def filter_data(data_df):
    ##格式化数据########
    # data_df['name'] = stock_names
    data_df['open'] = data_df['open'].astype(float)
    data_df['high'] = data_df['high'].astype(float)
    data_df['low'] = data_df['low'].astype(float)
    data_df['close'] = data_df['close'].astype(float)
    data_df['amplitude'] = data_df.apply(lambda x: round((x.high - x.low) / x.low, 2), axis=1).astype(float)
    # 过滤:振幅>10%,向下振幅>=5%,非ST，非停牌
    data_df = data_df.loc[lambda x: (x.amplitude >= 0.1) & ((x.close - x.low) / x.low >= 0.05) & (
            (x.high - x.close) / x.close >= 0.03) & (x.isST == '0') & (x.tradestatus == '1')]
    data_df['turn'] = round(data_df['turn'].astype(float), 2)
    data_df['pctChg'] = round(data_df['pctChg'].astype(float), 2)
    data_df['amount'] = data_df['amount'].astype(float) / 10000
    data_df['volume'] = data_df['volume'].astype(float) / 100
    data_df['peTTM'] = round(data_df['peTTM'].astype(float), 2)
    data_df['pbMRQ'] = round(data_df['pbMRQ'].astype(float), 2)
    data_df['pcfNcfTTM'] = round(data_df['pcfNcfTTM'].astype(float), 2)

    ##排序##
    data_df.sort_index(axis=1)
    data_df.sort_values(by=['amplitude'], inplace=True, ascending=False)

    return data_df


def download_data_by_day(date):
    # 获取指定日期的指数、股票数据
    stock_rs = bs.query_all_stock(date)
    stock_df = stock_rs.get_data()
    data_df = pd.DataFrame()
    # stock_names= []
    for code in stock_df["code"]:
        if code.startswith('sz.300'):
            print("Downloading :" + code + '...')
            #### 获取历史数据,先查询开始日期当天数据 ####
            # date:日期,code:代码,open:开盘价,high:最高价,low:最高价,close:收盘价,volume:成交量(股),amount:成交额(元),
            # adjustflag:复权状态(1:后复权,2:前复权,3:不复权),turn;换手率,tradestatus:交易状态(1：正常交易 0：停牌）,pctChg:涨跌幅(百分比),peTTM:滚动市盈率,pbMRQ:市净率,pcfNcfTTM:滚动市现率,isST:是否ST股(1是，0否)
            k_rs = bs.query_history_k_data_plus(code,
                                                "date,code,open,high,low,close,volume,amount,turn,tradestatus,pctChg,peTTM,pbMRQ,pcfNcfTTM,isST",
                                                start_date=date, end_date=date, frequency='d',
                                                adjustflag="3")
            data_df = data_df.append(k_rs.get_data())
    return data_df


if __name__ == '__main__':
    #### 登陆系统 ####
    bs.login()
    # 获取指定日期全部日线数据
    download_data('2020-11-09')
    #### 登出系统 ####
    bs.logout()
