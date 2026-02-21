n = list(map(int, input().split()))
avg = sum(n) / len(n)
count = 0 
for i in range(len(n)):
    if n[i] > avg:
        count += 1
print(count)
