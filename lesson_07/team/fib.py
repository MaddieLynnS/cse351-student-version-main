def fib(n):
    prev_num = 0
    num = 1
    for _ in range(n - 1):
        temp = number
        number = number + prev_num
        prev_num = temp
    return number

def rec_fib(n):
    #fib(10) = fib(9) + fib(8)
    if n <= 2:
        return 1
    return rec_fib(n - 1) + rec_fib(n - 2)


if __name__ == '__main__':
    pass