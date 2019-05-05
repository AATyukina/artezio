def decorator(funct, par='ttt'):
    print(par)
    def wrapper (a, b):
        def in_wrap(c):
            print (c)
            print (funct(a, b))
        return in_wrap
    return wrapper



def a (one, two):
    return one+two

a = decorator(a, par='uuu')(5, 7)
a(7)

