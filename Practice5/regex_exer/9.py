import re
s = input()
x = re.sub("([A-Z])", " \\1", s).strip()
print(x)