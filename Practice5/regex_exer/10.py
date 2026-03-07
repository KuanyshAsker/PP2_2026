import re
s = input()
x = re.sub("([A-Z])", "_\\1", s).lower().lstrip('_')
print(x)