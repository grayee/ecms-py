# -*- coding: utf-8 -*-

import baostock as bs
import pandas as pd
import datetime
import openpyxl
import os


def download_data(date):
    data_df = download_data_by_day(date)
    data_df = filter_data(data_df)
    #    print(data_df)
    #    rs_df = pd.DataFrame()
    #    begin_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    #    end_date = begin_date + datetime.timedelta(days=1)
    #    if end_date <= datetime.date.today():
    #        for row_index, row in data_df.iterrows():
    #            k_rs = get_history_k_data(row.code, end_date.strftime("%Y-%m-%d"))
    #            #print(k_rs.get_data().loc[0].low,row.low,row.code)
    #            #print(float(k_rs.get_data().loc[0].low)-row.low,row.code)
    #            rs_df = rs_df.append(row,ignore_index=False)
    #            rs_df = rs_df.append(k_rs.get_data())
    #

    print("当日过滤数据", data_df)
    write_to_excel(data_df, 'd:\\output-' + datetime.datetime.now().strftime('%Y-%m') + '-filter.xlsx', date)
    # 过滤上个交易日相关指标
    begin_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    basic_df = pd.DataFrame()
    for row_index, row in data_df.iterrows():
        if begin_date.isoweekday() == 1:
            day_step = -3
        else:
            day_step = -1

        # 上一个工作日
        last_work_day = begin_date + datetime.timedelta(days=day_step)
        last_rs = get_history_k_data(row.code, last_work_day.strftime("%Y-%m-%d"))

        last_st = last_rs.get_data().loc[0]
        # 当日最低价小于等于上日最低价，当日收盘价高于上日最高价,上一日涨幅或跌幅<10%
        if row.low <= float(last_st.low) and row.close > float(last_st.high) and abs(
                float(last_st.close) - float(last_st.open)) < 10:
            # 名称
            basic_rs = bs.query_stock_basic(code=row.code)
            basic_df = basic_df.append(basic_rs.get_data())

    data_df = pd.merge(data_df, basic_df, how='inner', on=['code'])
    # 改变数据列的顺序
    data_df = data_df[['date', 'code', 'code_name','pctChg', 'amplitude', 'turn', 'close', 'open', 'high', 'low', 'amount','peTTM']]
    # 输出
    print(data_df)
    write_to_excel(data_df, 'd:\\output-' + datetime.datetime.now().strftime('%Y-%m') + '.xlsx', date)


def write_to_excel(data, file_name, sheet_name):
    """
    不改变原有Excel的数据，新增sheet。
    注：
        使用openpyxl操作Excel时Excel必需存在，因此要新建空sheet
        无论如何sheet页都会被新建，只是当sheet_name已经存在时会新建一个以1结尾的sheet，如：test已经存在时，新建sheet为test1，以此类推
    :param file_name: 文件路径
    :param data: DataFrame数据
    :param sheet_name: 新增的sheet名称
    :return:
    """
    # render dataframe as html
    excel_writer = pd.ExcelWriter(file_name, engine='openpyxl')

    if os.path.exists(excel_writer.path):
        book = openpyxl.load_workbook(excel_writer.path)
        excel_writer.book = book

    data.to_excel(excel_writer=excel_writer, sheet_name=sheet_name, index=None)
    excel_writer.save()
    excel_writer.close()

def filter_data(data_df):
    #data_df = data_df[data_df['tradestatus'] == 1]
    ##格式化数据########
    data_df['open'] = data_df['open'].astype(float)
    data_df['high'] = data_df['high'].astype(float)
    data_df['low'] = data_df['low'].astype(float)
    data_df['close'] = data_df['close'].astype(float)
    data_df['preclose'] = data_df['preclose'].astype(float)
    data_df['amplitude'] = data_df.apply(lambda x: round((x.high - x.low) / x.low, 2), axis=1).astype(float)


    # 过滤:振幅>8%,向下振幅>=5%,向上振幅大>%2,涨幅>=%5,非ST，非停牌
    data_df = data_df.loc[lambda x: (x.amplitude >= 0.08) & ((x.close - x.low) / x.low >= 0.05) & (
            (x.high - x.close) / x.close > 0.02) & (x.close > x.preclose) & (x.isST == '0') & (
                                                x.tradestatus == '1')]

    data_df['pctChg'] = data_df['pctChg'].astype(float)
    data_df['turn'] = round(data_df['turn'].astype(float), 2)
    data_df['pctChg'] = round(data_df['pctChg'], 2)
    data_df['amount'] = data_df['amount'].astype(float) / 10000
    data_df['volume'] = data_df['volume'].astype(float) / 100
    data_df['peTTM'] = round(data_df['peTTM'].astype(float), 2)
    data_df['pbMRQ'] = round(data_df['pbMRQ'].astype(float), 2)
    data_df['pcfNcfTTM'] = round(data_df['pcfNcfTTM'].astype(float), 2)

    ##排序##
    data_df.sort_index(axis=1)
    data_df = data_df.sort_values(by=['amplitude'], ascending=False)
    # 重置索引
    data_df.reset_index(drop=True, inplace=True)
    return data_df


def download_data_by_day(date):
    # 获取指定日期的指数、股票数据
    stock_rs = bs.query_all_stock(date)
    stock_df = stock_rs.get_data()
    data_df = pd.DataFrame()
    # stock_names= []
    for code in stock_df["code"]:
        if code.startswith('sz.300'): #or code.startswith('sz.00') or code.startswith('sh.60'):
            print("Downloading :" + code + '...')
            k_rs = get_history_k_data(code, date)
            data_df = data_df.append(k_rs.get_data())
    return data_df


def get_history_k_data(code, date):
    #### 获取历史数据,先查询开始日期当天数据 ####
    # date:日期,code:代码,open:开盘价,high:最高价,low:最高价,close:收盘价,volume:成交量(股),amount:成交额(元),
    # adjustflag:复权状态(1:后复权,2:前复权,3:不复权),turn;换手率,tradestatus:交易状态(1：正常交易 0：停牌）,pctChg:涨跌幅(百分比),peTTM:滚动市盈率,pbMRQ:市净率,pcfNcfTTM:滚动市现率,isST:是否ST股(1是，0否)
    k_rs = bs.query_history_k_data_plus(code,
                                        "date,code,open,high,low,preclose,close,volume,amount,turn,tradestatus,pctChg,peTTM,pbMRQ,pcfNcfTTM,isST",
                                        start_date=date, end_date=date, frequency='d',
                                        adjustflag="3")
    return k_rs


if __name__ == '__main__':
    #### 登陆系统 ####
    bs.login()
    # 获取指定日期全部日线数据
    download_data('2020-12-31')
    #### 登出系统 ####
    bs.logout()
