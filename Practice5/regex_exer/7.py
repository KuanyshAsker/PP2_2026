import re
s = input()
x = re.sub("_([a-zA-Z])", lambda m: m.group(1).upper(), s)
print(x)
