# 这是一个注释：print 是一个函数
print("hello world")

age = 30
name = "Gray.Zhang"

print("{} wan {} years old when 2018 years".format(name,age))
print('Why is {} playing with that python?'.format(name))

# 对于浮点数 '0.333' 保留小数点(.)后三位
print('{0:.3f}'.format(1.0/3))
# 使用下划线填充文本，并保持文字处于中间位置
# 使用 (^) 定义 '___hello___'字符串长度为 11
print('{0:_^11}'.format('hello'))
# 基于关键词参数输出 'Swaroop wrote A Byte of Python'
print('{name} wrote {book}'.format(name='Swaroop', book='A Byte of Python'))

#注意 print 总是会以一个不可见的“新一行”字符（ \n ）结尾
print('a', end=' ')
print('b', end=' ')
print('c')
# 通过转义符（ \n ） 开始新一行
print('This is the first line\nThis is the second line')
#一个放置在末尾的反斜杠表示字符串将在下一行继续，但不会添加新的一行
print("This is the first sentence. \
This is the second sentence.")
#在字符串前增加r 或 R 来指定一个 原始（Raw） 字符串
print(r"Newlines are indicated by \n")