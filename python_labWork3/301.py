n = int(input())
flag = True 
while n > 0:
    digit = n % 10
    if digit % 2 != 0:
        flag = False
        break
    n = n // 10
if flag:
    print("Valid")
else:
    print("Not valid")