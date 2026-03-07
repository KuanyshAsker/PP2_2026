import re 
txt = input()
x = re.findall("[a-z]+(?:_[a-z]+)+", txt)
print(x)