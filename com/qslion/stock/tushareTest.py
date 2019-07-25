# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import tushare as ts
import pathlib
import datetime
import os
import matplotlib.pyplot as plt

print("Tushare version is :【{}】 , Pandas version is  ; 【{}】".format(ts.__version__, pd.__version__))

# 设置专业版token
my_pro_token = "89c2772fb6e5afa63fcac1ad65f53ce99d2db12314a383ec7c35d3ea"
ts.set_token(my_pro_token)
# 初始化pro接口，带token方法：ts.pro_api('your token')
pro = ts.pro_api("89c2772fb6e5afa63fcac1ad65f53ce99d2db12314a383ec7c35d3ea")

today = datetime.datetime.now().strftime("%Y%m%d")
stock_list_file = "d:/data/stock_list_{}.xlsx".format(today)
# 判断文件是否存在
try:
    if not pathlib.Path(stock_list_file).exists():
        raise FileNotFoundError
except FileNotFoundError:
    # 文件不存在
    stock_basic_fields = 'ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs'
    # 查询当前所有正常上市交易的股票列表,https://tushare.pro/document/
    stock_list = pro.stock_basic(exchange='', list_status='L', fields=stock_basic_fields)
    print(stock_list)
    stock_list.to_excel(stock_list_file)
else:
    # 存在
    print("file existed !!!!")
    #os.remove(stock_list_file)

tc_filename = 'd:/data/trade_cal.csv'
if not os.path.exists(tc_filename):
    # 获取各大交易所交易日历数据,默认提取的是上交所(交易所 SSE上交所 SZSE深交所,0休市 1交易)
    trade_cal = pro.trade_cal(exchange='', start_date='20190101', end_date='20191231')
    trade_cal.to_csv(tc_filename)

df = ts.pro_bar(ts_code='000001.SZ', adj='qfq', start_date='20190101', end_date='20190724')
#按照日期排序
df = df.sort_values(by='trade_date', ascending=True)

print(df[["trade_date","close","amount"]])

df[["trade_date","close","amount"]].T.loc["close"].plot(kind='line', label='Algeria')
plt.legend(loc='upper left')
plt.show()