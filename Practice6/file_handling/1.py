numbers = [1, 2, 3, 4, 5]

map_use = list(map(lambda x: x * 2, numbers))
filter_use = list(filter(lambda x: x % 1 == 0, numbers))

for number in map_use:
    print(number, end=" ")
print("\n")
for number in filter_use:
    print(number, end=" ")