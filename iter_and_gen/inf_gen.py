def inf_gen(number=0):
    while True:
        yield number


g = inf_gen(5)
for item in range(10):
    print(g.next())