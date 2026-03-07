import re
s = input()
x = re.match("ab*", s)
print("Match" if x else "No match")