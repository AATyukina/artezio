def xr(end):
    current = 0
    while True:
        yield current
        current += 1
        if current == end:
            raise StopIteration

    # for i in range(end):
    #     yield end


# def xr(start, end):
#     current = start
#     while True:
#         yield current
#         current += 1
#         if current == end:
#             raise StopIteration


for item in xr(10):
    print(item)

num = xr(3)
print("Items in xr(3): %d, %d, %d" % (num.next(), num.next(), num.next()))
print(num.next())
