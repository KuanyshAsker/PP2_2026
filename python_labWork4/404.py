def squares_from_a_to_b(a, b):
    for i in range(a, b + 1):
        yield i ** 2
rang = list(map(int, input().split()))
a = rang[0]
b = rang[1]
for num in squares_from_a_to_b(a, b):
    print(num)
