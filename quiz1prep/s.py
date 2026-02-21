l = int(input()) # 1 > 0
r = int(input()) # 3 > 2
n = list(map(int, input().split()))
m = n[l-1:r -1 +1]
m.reverse()
print(n[:l - 1 - 1 + 1] + m + n[r - 1 + 1:])