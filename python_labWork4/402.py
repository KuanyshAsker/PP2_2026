def even_numbers(n):
    i = 0
    while i <= n:
        yield i 
        i += 2
n = int(input())
l = []
for num in even_numbers(n):
    l.append(num)
    l.append(",")
l.pop()
for x in l:
    print(x, end="")
    