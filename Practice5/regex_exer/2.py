import re 
txt = input()
x = re.match("ab{2,3}", txt)
if x:
    print("Match found")
else:
    print("Not found")