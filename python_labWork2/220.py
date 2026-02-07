import sys
input = sys.stdin.readline
n = int(input())
d = {}
for i in range(n):
    p = input().split()
    k = p[1]
    if p[0] == "set":
        v = p[2]
        d[k] = v
    else:
        if k in d:
            print(d[k])
        else:
            print(f"KE: no key {k} found in the document")