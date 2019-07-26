# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = [1, 3, 5, np.nan, 6, 8]
s = pd.Series(data)

print(s)
df = pd.DataFrame(data)
print(df)

# 通过传递numpy数组，使用datetime索引和标记列来创建DataFrame
dates = pd.date_range('20170101', periods=10)
print(dates)

print("--" * 16, "datetime索引和标记列表格", "--" * 16)
df = pd.DataFrame(np.random.randn(10, 4), index=dates, columns=list('ABCD'))
print(df)
print("--" * 16, "行列转置", "--" * 16)
print(df.T)
print("--" * 16, "axis轴（1行0列）排序", "--" * 16)
print(df.sort_index(axis=1, ascending=False))
print("--" * 16, "按某一列值排序", "--" * 16)
print(df.sort_values(by='B'))
print("--" * 16, "按列标签获取", "--" * 16)
print(df['A'], "\n", df.A)

df = pd.DataFrame(np.random.randn(10, 5), index=pd.date_range('20101229', periods=10), columns=list('ABCDE'))
print(df)
df.plot()


df = pd.DataFrame(np.random.rand(10,4),columns=['a','b','c','d'])
df.plot.bar(stacked=True)
df.plot.barh(stacked=True)


df = pd.DataFrame(3 * np.random.rand(4), index=['a', 'b', 'c', 'd'], columns=['x'])
df.plot.pie(subplots=True)

plt.show()
