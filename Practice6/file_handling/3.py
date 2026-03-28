items = ["apple", "banana", "mango"]
for index, item in enumerate(items):
    print(index, item) #enumerate example

print("\n")

students = ["Alyssa", "Glenn", "Noah"]
scores = [67, 78, 89]

for name, score in zip(students, scores):
    print(name, score) #zip example