n = int(input())
numbers = list(map(int, input().split()))
m = numbers[0]
for i in range(1, len(numbers)):
    if numbers[i] > m:
        m = numbers[i]
print(m)

