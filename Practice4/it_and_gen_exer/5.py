def func(n):
    for i in range(n, -1, -1):
        yield i
n = int(input())
for x in func(n):
    print(x, end=" ")