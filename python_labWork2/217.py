n=int(input())
nums=[]
for i in range(n):
    nums.append(input())
used=[]
answer=0
for i in range(n):
    if nums[i] in used:
        continue
    count=0
    for j in range(n):
        if nums[j]==nums[i]:
            count+=1
    if count==3:
        answer+=1
    used.append(nums[i])
print(answer)
