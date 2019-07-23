# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib as mpl
import math
import matplotlib.pyplot as plt

# 解决中文乱码
mpl.rcParams['font.sans-serif'] = ['SimHei']

input_values = [1, 2, 3, 4, 5]

squares = list(map(lambda x: x * x, input_values))
sqrts = list(map(lambda x: math.sqrt(x), input_values))

fig = plt.figure(figsize=(10, 5))  # 指定画图区大小（长，宽）

ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)

# plot(x轴,y轴)方法画图
ax1.plot(input_values, squares, linewidth=2, label="平方")
ax1.plot(input_values, sqrts, linewidth=1, c="red", label="开方")
ax1.legend(loc='upper left') #loc指定legend方框的位置,loc = 'best'/'upper right'/'lower left'等，print(help(plt.legend))查看用法
#ax1.set_xticks(rotation=45)  # 设置x轴上横坐标旋转角度
# 设置图表标题，并给坐标轴就加上标签
ax1.set_title(u"数值平方", fontsize=24)
ax1.set_xlabel(u"数值", fontsize=14)
ax1.set_ylabel(u"数值平方", fontsize=14)
# # 设置刻度标记大小
ax1.tick_params(axis="both", labelsize=10)

ax2.plot(np.random.randint(1,5,5), np.arange(5)) #子图画图
ax2.set_xlabel('Rotten Tomatoes')
ax2.set_ylabel('Fandango')

plt.show()
