import re #Regular Expression is a sequence of characters that forms a search pattern.

import re
txt = "The rain in Spain"
x = re.search("^The.*Spain$", txt) #starts with "The" and ends with "Spain"

# RegEx functions 
#findall	Returns a list containing all matches
#search     Returns a Match object if there is a match anywhere in the string
#split	    Returns a list where the string has been split at each match
#sub	    Replaces one or many matches with a string

import re
txt = "The rain in Spain"
x = re.findall("ai", txt)
print(x) #Print a list of all matches

import re
txt = "The rain in Spain"
x = re.findall("Portugal", txt)
print(x) #Return an empty list if no match was found

import re #Search for the first white-space character in the string:
txt = "The rain in Spain"
x = re.search("\s", txt)
print("The first white-space character is located in position:", x.start())

import re 
txt = "The rain in Spain"
x = re.search("Portugal", txt)
print(x) #Make a search that returns no match

import re
txt = "The rain in Spain"
x = re.split("\s", txt)
print(x) #Split at each white-space character:

import re
txt = "The rain in Spain"
x = re.split("\s", txt, 1)
print(x) #Split the string only at the first occurrence

import re
txt = "The rain in Spain"
x = re.sub("\s", "9", txt)
print(x) #Replace every white-space character with the number 9:

import re
txt = "The rain in Spain"
x = re.sub("\s", "9", txt, 2)
print(x) #Replace the first 2 occurrences

import re
txt = "The rain in Spain"
x = re.search("ai", txt)
print(x) #this will print an object
#Do a search that will return a Match Object 

import re
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.span()) #regular expression looks for any words that starts with an upper case "S"

import re
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.string) #Print the string passed into the function

import re
txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.group()) #regular expression looks for any words that starts with an upper case "S"





