def func(n):
    for i in range(n):
        yield (i + 1) ** 2
n = int(input())
for x in func(n):
    print(x, end=" ")