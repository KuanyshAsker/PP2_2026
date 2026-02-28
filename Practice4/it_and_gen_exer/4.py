def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2
n = int(input())
for x in squares(n):
    print(x, end=" ")    