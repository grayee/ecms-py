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

print("tushare version is :{} , pandes version is  ; {} , elasticsearch version is ::{} ".format(ts.__version__,pd.__version__,elastic.__version__))

s = pd.Series([1,3,5,np.nan,6,8])
print(s)

dates = pd.date_range('20170101', periods=7)
print(dates)
print("--"*16)
df = pd.DataFrame(np.random.randn(7,4), index=dates, columns=list('ABCD'))
print(df)


# 连接本地ES
es = elastic.Elasticsearch("localhost:9200")
if  not es.indices.exists('my-stock') :
    es.indices.create(index='my-stock', ignore=400)

#大盘指数行情列表
df = ts.get_index()
jsonArray = df.to_json(orient='records')

#es.index('my-stock',"indexType",jsonArray);

es.bulk(index="my-stock",doc_type="indexType",body=[{"any":"data02","timestamp":datetime.now()},{"any":"data03","timestamp":datetime.now()}])


print(jsonArray)