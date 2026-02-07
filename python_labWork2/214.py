n=int(input())
a=list(map(int,input().split()))
best=a[0]
best_count=0
for i in range(n):
    count=0
    for j in range(n):
        if a[j]==a[i]:
            count+=1
    if count>best_count or (count==best_count and a[i]<best):
        best_count=count
        best=a[i]
print(best)
