import re
s = input()
x = re.findall("\\b[A-Z][a-z]*\\b", s)
print(x)