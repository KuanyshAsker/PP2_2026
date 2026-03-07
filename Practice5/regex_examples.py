#research()
import re
text = "My phone number is 7771234567"
match = re.search(r"\d+", text)
print(match.group()) #Finds the first match of a pattern anywhere in the string

#re.findall()
import re
text = "I bought 3 apples, 5 bananas, and 10 oranges"
numbers = re.findall(r"\d+", text)
print(numbers) #Returns all matches as a list

#re.split()
import re
text = "apple,banana;orange grape"
result = re.split(r"[ ,;]", text)
print(result) #Splits a string using a regex pattern as the separator

#re.sub()
import re
text = "My number is 7771234567"
result = re.sub(r"\d", "*", text)
print(result) #Replaces matches with another string


