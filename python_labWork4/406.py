def fibonac(n):
    a, b = 0, 1
    for i in range(n):
        yield a
        a, b = b, a + b
n = int(input())
print(",".join(map(str, fibonac(n))))