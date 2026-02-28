def even_numbers(n):
    for i in range(0, n + 1, 2):
        yield i
n = int(input())
temp = even_numbers(1000000)
for _ in range(n // 2):
    print(next(temp), end=",")
print(next(temp))