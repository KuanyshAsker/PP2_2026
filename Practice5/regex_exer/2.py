import re
s = input()
x = re.match("ab{2,3}", s)
print("Match" if x else "No match")