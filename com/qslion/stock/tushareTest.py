# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import tushare as ts
import elasticsearch as elastic
from datetime import datetime

print("Tushare version is :【{}】 ,\nPandes version is  ; 【{}】, \nElasticsearch version is :【{}】 "
      .format(ts.__version__, pd.__version__, elastic.__version__))

# 设置专业版token
my_pro_token = "89c2772fb6e5afa63fcac1ad65f53ce99d2db12314a383ec7c35d3ea"
ts.set_token(my_pro_token)
# 初始化pro接口，带token方法：ts.pro_api('your token')
pro = ts.pro_api()
# 查询当前所有正常上市交易的股票列表,https://tushare.pro/document/
stock_list = pro.stock_basic(exchange='', list_status='L',
                             fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
print(stock_list)

# 获取各大交易所交易日历数据,默认提取的是上交所(交易所 SSE上交所 SZSE深交所,0休市 1交易)
pro.trade_cal(exchange='', start_date='20190101', end_date='20191231')

# 获取上市公司基础信息
company_df = pro.stock_company(exchange='SZSE',
                               fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province')

dates = pd.date_range('20170101', periods=7)
print(dates)
print("--" * 16)
df = pd.DataFrame(np.random.randn(7, 4), index=dates, columns=list('ABCD'))
print(df)

# 连接本地ES
# es = elastic.Elasticsearch("localhost:9200")
# if  not es.indices.exists('my-stock') :
#     es.indices.create(index='my-stock', ignore=400)

# 大盘指数行情列表
df = ts.get_index()
jsonArray = df.to_json(orient='records')

# es.index('my-stock',"indexType",jsonArray);

# es.bulk(index="my-stock",doc_type="indexType",body=[{"any":"data02","timestamp":datetime.now()},{"any":"data03","timestamp":datetime.now()}])


print(jsonArray)
