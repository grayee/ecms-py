# -*- coding: UTF-8 -*-
a= "hello"
b = list(a)
print(list(b))

del b[2]
print (b)
b[2]='t'
print (b)

b[2:4]=list('yy')
print(b)