with open("1.txt", "a") as x: 
    x.write("\nWoops! I added new line.\n")
with open("1.txt") as x:
    print(x.read())