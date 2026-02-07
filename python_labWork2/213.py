n = int(input())
if n < 2: 
    print("No")
else: 
    i = 2 
    while i * i <= n: 
        if n % i == 0:
            print("No")
            break
        i += 1
    else: 
        print("Yes")