import re
s = input()
x = re.sub("[ ,.]", ":", s)
print(x)