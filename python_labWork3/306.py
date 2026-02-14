class Shape: 
    def area(self):
        return 0
class Rectangle(Shape):
    def __init__(self, length, width):
        self.length = length
        self.width = width 
    def area(self):
        return self.length * self.width 
length, width = map(int, input().split())
rect = Rectangle(length, width)
print(rect.area())