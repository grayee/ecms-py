def reverse(text):
    return text[::-1]

def is_palindrome(text):
    return text == reverse(text)

class ShortInputException(Exception):
    '''一个由用户定义的异常类'''
    def __init__(self, length, atleast):
        Exception.__init__(self)
        self.length = length
        self.atleast = atleast

try:
    something = input("Enter text:")
    if len(something) < 3:
        raise ShortInputException(len(something), 3)
except ShortInputException as ex:
    print(('ShortInputException: The input was ' +
    '{0} long, expected at least {1}')
    .format(ex.length, ex.atleast))
except KeyboardInterrupt:
    print("you cancelled the operation")
else:
    print("you entered:{}".format(something))
if is_palindrome(something):
    print("Yes,it is a palindrome")
else:
    print("No,it is not a palindrome")