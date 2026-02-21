def square_of_numbers(n):
    i = 1
    while i <= n:
        yield i ** 2
        i += 1 
n = int(input())
for num in square_of_numbers(n):
    print(num)
