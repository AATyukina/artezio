# -*- coding: utf-8 -*-

class One:
    def __init__(self, arg=int):
        if type(arg) == int:
            self.argument = arg
        else:
            raise TypeError ('Incorrent type of argument')

    @staticmethod
    def total(arg):
        return arg + 10

    def __add__(self, n):
        return One(self.argument + n.argument)

    def __str__(self):
        return '%s %d' % ("Аргумент =", self.argument)

class Two:
    @staticmethod
    def total(st=str):
        return len(st)


if __name__ == "__main__":
    o1 = One(1)
    o2 = One(3)
    o3 = o1+o2
    print(o3)
    print(One.total(56))
    print(Two.total("lflflflf"))