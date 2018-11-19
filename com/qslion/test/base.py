# ------------------------------------if -------------------------------------------------------------
number = 23
guess = int(input('Enter an integer : '))
if guess == number:
    # 新块从这里开始
    print('Congratulations, you guessed it.')
    print('(but you do not win any prizes!)')
    # 新块在这里结束
elif guess < number:
    # 另一代码块
    print('No, it is a little higher than that')
    # 你可以在此做任何你希望在该代码块内进行的事情
else:
    print('No, it is a little lower than that')
    # 你必须通过猜测一个大于（>）设置数的数字来到达这里。
print('if Done')
# 这最后一句语句将在
# if 语句执行完毕后执行。

# ---------------------------------while loop------------------------------------------------------
running = True

while running:
    guess = int(input("Enter an integer:"))
    if guess == number:
        print("congratulations,you guesses it. ")
        # 终止while 循环
        running = False

    elif guess < number:
        print("No,it is a little higher than that.")
    else:
        print("No,it is a little lower than that.")
else:
    print("the while loop is over")
    # 这里可以做任何想做的事情

while True:
    s = input('Enter something : ')
    if s == 'quit':
        break
    if len(s) < 3:
        print('Too small')
        continue
    print('Input is of sufficient length')

print("while done")
# ---------------------------------for loop -------------------------------------------------------
for i in range(1, 5):
    print(i)
else:
    print("The for loop is over,list rang :{}".format(list(range(5))))


# ---------------------------------function ----------------------------------------------------------
def say_hello(a, b=5):
    if a > b:
        print(a, 'is maximum')
    elif a == b:
        print(a, 'is equal to ', b)
    else:
        print(b, 'is maximum')
    # 该块属于一个函数
    print('hello world')


# 函数结束

# 函数调用
say_hello(1)
say_hello(a=8, b=9)

#可变参数
def total(a=5, *numbers, **phonebook):
    print('a', a)
    # 遍历元组(Tuple)中的所有项目
    for single_item in numbers:
        print('single_item', single_item)

    # 遍历字典（Dictionary）中的所有项目
    for first_part, second_part in phonebook.items():
        print(first_part, second_part)


print(total(10, 1, 2, 3, jack=1123, john=2231, inge=234))

# return 用于从函数中返回，也就是中断函数;DocStrings
def maximum(x, y):
    '''Prints the maximum of two numbers.打印两个数值中的最大数。

    The two values must be integers.这两个数都应该是整数'''
    # 如果可能，将其转换至整数类型
    x = int(x)
    y = int(y)

    if x > y:
        return x
    elif x == y:
        return 'The numbers are equal'
    else:
        return y

print(maximum(2, 3))
print(maximum.__doc__)

help(maximum)