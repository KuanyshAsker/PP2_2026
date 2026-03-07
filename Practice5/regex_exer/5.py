import re 
txt = input()
x = re.match("^a+b$", txt)
print(x)