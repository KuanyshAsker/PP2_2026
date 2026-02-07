n = int(input())
numbers = list(map(int, input().split()))
m = numbers[0]
for x in range(1, len(numbers)):
    if numbers[x] > m: 
        m = numbers[x]
print(numbers.index(m) + 1)