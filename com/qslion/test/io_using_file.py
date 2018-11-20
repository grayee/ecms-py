poem = '''\
Programming is fun
When the work is done
if you wanna make your work also fun:
use Python!
'''
try:
    # 打开文件以编辑（'w'riting）
    f = open('poem.txt', 'wt',encoding="utf-8")
    # 向文件中编写文本
    f.write(poem)
    f.write(u"Imagine non-English language here,哈哈")
except IOError:
    print("could not find the file")
finally:
    if f:
        # 关闭文件
        f.close()
    print("(Cleaning up: Closed the file)")

# 如果没有特别指定，
# 将假定启用默认的阅读（'r'ead） 模式
with open('poem.txt',encoding="utf-8") as f:
    while True:
        line = f.readline()
        # 零长度指示 EOF
        if len(line) == 0:
            break
        # 每行（`line`） 的末尾
        # 都已经有了换行符
        # 因为它是从一个文件中进行读取的
        print(line, end='')