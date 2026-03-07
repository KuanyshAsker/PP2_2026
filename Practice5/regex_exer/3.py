import re
s = input()
x = re.findall("\\b[a-z]+_[a-z]+\\b", s)
print(x)