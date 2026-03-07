import re
txt = input()
x = re.match("ab*", txt)
if x:
    print("Match found")
else: 
    print("Not found")