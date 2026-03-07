import re
s = input()
x = re.findall("[A-Z][a-z]*", s)
print(x)