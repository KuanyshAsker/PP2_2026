import re
s = input()
x = re.search("^a.*b$", s)
print("Match" if x else "No match")