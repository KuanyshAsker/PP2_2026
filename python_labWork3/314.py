n=int(input())
a=list(map(int,input().split()))
q=int(input())
for _ in range(q):
    parts=input().split()
    op=parts[0]
    if op=="add":
        x=int(parts[1])
        a=[v+x for v in a]
    elif op=="multiply":
        x=int(parts[1])
        a=[v*x for v in a]
    elif op=="power":
        x=int(parts[1])
        a=[v**x for v in a]
    else:
        a=[abs(v) for v in a]
print(*a)
