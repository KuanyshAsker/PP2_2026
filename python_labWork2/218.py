n = int(input())
arr = []
for i in range(n):
    arr.append(input())
sorted_arr = arr[:]
sorted_arr.sort()
printed = []
for s in sorted_arr:
    if s not in printed:
        for i in range(n):
            if arr[i] == s:
                print(s,i+1)
                break
        printed.append(s)
