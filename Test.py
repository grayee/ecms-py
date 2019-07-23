# -*- coding: UTF-8 -*-
import numpy as np

import datetime
import random

a= "hello"
b = list(a)
print(list(b))

del b[2]
print (b)
b[2]='t'
print (b)

b[2:4]=list('yy')
print(b)

# for i in range(10):
#     print(i)

#####numpy########
a = [1, 2, 4, 3]  # vector
b = np.array(a)  # array([1, 2, 4, 3])
print(type(b))  # <type 'numpy.ndarray'>
print(b)
print(b[0:3])
print(a)

b.shape                   # (4,) 返回矩阵的（行数，列数）或向量中的元素个数
b.argmax()                  # 2 返回最大值所在的索引
b.max()                     # 4最大值
b.min()                     # 1最小值
b.mean()                    # 2.5平均值
print(b.shape,b.dtype ,b.argmax() ,b.max()  ,b.min(),b.mean())

c = [[1, 2], [3, 4]]    # 二维列表
d = np.array(c)             # 二维numpy数组
d.shape                     # (2, 2)
d[1,1]                      #4,矩阵方式按照行、列获取元素
d.size                      # 4 数组中的元素个数
d.max(axis=0)               # 找维度0，也就是最后一个维度上的最大值，array([3, 4])
d.max(axis=1)               # 找维度1，也就是倒数第二个维度上的最大值，array([2, 4])
d.mean(axis=0)              # 找维度0，也就是第一个维度上的均值，array([ 2.,  3.])
d.flatten()                 # 展开一个numpy数组为1维数组，array([1, 2, 3, 4])
np.ravel(c)               # 展开一个可以解析的结构为1维数组，array([1, 2, 3, 4])
print(d.max(axis=1)  )

#二维
matrix = np.array([
                [5,10,15],
                [20,25,30],
                [35,40,45]
                ])
print(matrix.sum(axis=1))  #指定维度axis=1，即按行计算
print(matrix.sum(axis=0))  #指定维度axis=0，即按列计算

print(matrix[:,1])  #[10 25 40]取出所有行的第一列
print(matrix[:,0:2])   #取出所有行的第一、第二列
print(matrix == 25)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print (now)

for i in range(0, 10):
    nowTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S");  # 生成当前时间
    randomNum = random.randint(0, 100)  # 生成的随机整数n，其中0<=n<=100
    if randomNum <= 10:
       randomNum = str(0) + str(randomNum)
    uniqueNum = str(nowTime) + str(randomNum)
    print(uniqueNum)