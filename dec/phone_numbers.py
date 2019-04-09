def wrapper(f):
    def make_format(l):
        return '{index} {first} {second}'.format(index='+91', first=l[-10: -5], second=l[-5:])
    def fun(l):
        return f(map(make_format, l[0:]))
    return fun

@wrapper
def sort_phone(l):
    print '\n'.join(sorted(l))

if __name__ == '__main__':
    l = [raw_input() for _ in range(int(input()))]
    sort_phone(l)