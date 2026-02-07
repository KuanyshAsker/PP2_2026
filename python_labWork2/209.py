n = int(input())
numbers = list(map(int, input().split()))
m = numbers[0]
for i in range(1, len(numbers)):
    if numbers[i] > m:
        m = numbers[i]
k = numbers[0]
for i in range(1, len(numbers)):
    if numbers[i] < k:
        k = numbers[i]
for i in range(len(numbers)):
    if numbers[i] == m:
        numbers[i] = k
for x in numbers:
    print(x, end=" ")
