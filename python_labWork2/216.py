n=int(input())
a=list(map(int,input().split()))
seen=[]
for x in a:
    if x not in seen:
        print("YES")
        seen.append(x)
    else:
        print("NO")
