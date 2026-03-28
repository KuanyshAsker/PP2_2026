from functools import reduce

numbers = [1, 2, 3, 4, 5]
reduce_use = reduce(lambda x, y: x + y, numbers)
print(reduce_use) #combines all the values into one