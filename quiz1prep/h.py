class Person:
    def __init__(self, name, age, country="Almaty"):
        self.name = name 
        self.age = age
        self.country = country
    def greet(self):
        print("Hello", self.name)
class Student(Person):
    pass
p2 = Student("Maksat", 20, "Taldykorgan")
print(p2.name, p2.age, p2.country)
p1 = Person("Kuanysh", 19)
print(p1.name, p1.age, p1.country)
p1.greet()