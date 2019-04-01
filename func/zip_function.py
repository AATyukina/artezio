def zip (*args):

    tmp_size = []
    un = []

    for item in args:
        tmp_size.append(len(item))
    s = max(tmp_size)

    for i in range(s):
        tmp = []

        for item in args:
            if i >= len(item):
                tmp.append(None)
            else:
                tmp.append(item[i])

        un.append(tmp)

    return un

print(zip([1, 2, 3], ['a', 'b', 'c'], [7, 8, 9]))
print(zip([1, 2, 3], ['a', 'b', 'c'], [7, 8]))
