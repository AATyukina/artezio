class Figure:
    def __init__(self, color="blue"):
        self.color = color

    def count_area(self):
        pass

    def __str__(self):
        return '%s %s' % ("Color =", self.color)


class Square(Figure):
    def __init__(self, color, side=0):
        Figure.__init__(self, color)
        self.side = side

    def count_area(self):
        return self.side ** 2

    def __str__(self):
        return Figure.__str__(self) + '\n%s %d' % ("Side =", self.side)


class Round(Figure):
    def __init__(self, color, radius=0):
        Figure.__init__(self, color)
        self.radius = radius

    def count_area(self):
        return 3.14 * self.radius ** 2

    def __str__(self):
        return Figure.__str__(self) + '\n%s %d' % ("Radius =", self.radius)


class Triangle(Figure):
    def __init__(self, color, side1=0, side2=0, side3=0):
        Figure.__init__(self, color)
        self.side1 = side1
        self.side2 = side2
        self.side3 = side3

    def count_area(self):
        p = (self.side1 + self.side2 + self.side3)/2
        return (p*(p - self.side1)*(p - self.side2)*(p - self.side3)) ** 0.5

    def __str__(self):
        return Figure.__str__(self) + '\n%s %d, %d, %d' % ("Sides =", self.side1, self.side2, self.side3)


if __name__ == "__main__":
    sq = Square("red", 10)
    print(sq)
    print (sq.count_area())

    tr = Triangle("green", side1=4, side2=7, side3=9)
    print (tr)
    print(tr.count_area())

    r = Round("yellow", 5)
    print(r)
    print(r.count_area())