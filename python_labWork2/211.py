n, l, r = map(int, input().split())
numbers = list(map(int, input().split()))
numbers[l - 1:r] = numbers[l - 1:r][::-1]
print(*numbers)