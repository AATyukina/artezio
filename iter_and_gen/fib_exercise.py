def fib():
    a = 1
    b = 1
    yield a
    yield b
    while True:
        a += b
        yield a
        a, b = b, a