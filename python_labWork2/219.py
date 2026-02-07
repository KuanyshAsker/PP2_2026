n = int(input())
names = []
counts = []
for i in range(n):
    s,k = input().split()
    k = int(k)
    if s in names:
        idx = names.index(s)
        counts[idx] += k
    else:
        names.append(s)
        counts.append(k)
for i in range(len(names)):
    for j in range(i+1,len(names)):
        if names[i] > names[j]:
            names[i],names[j] = names[j],names[i]
            counts[i],counts[j] = counts[j],counts[i]
for i in range(len(names)):
    print(names[i], counts[i])
