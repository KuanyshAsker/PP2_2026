import math
sides = int(input("Input number of slides: "))
length = float(input("Input the length of the slides: "))
area = int(sides * length * length / (math.tan(math.pi / sides) * 4))
print("The area of polygon is:", area)