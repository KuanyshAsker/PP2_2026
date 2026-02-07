n = int(input())
x = 2
for i in range(n): 
    if x**i <= n:
        print(x**i, end=" ")
