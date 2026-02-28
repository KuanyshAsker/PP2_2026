def func(n):
    for i in range(0, n + 1, 12):
        yield i
n = int(input())
for x in func(n):
    print(x, end=" ")