import re 
txt = input()
x = re.sub("[ ,.]", ":", txt)
print(x)