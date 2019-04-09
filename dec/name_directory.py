import operator
from operator import itemgetter

def person_lister(f):
    def inner(people):
        return list(map(f, sorted(people, key=itemgetter(2))))
    return inner


@person_lister
def name_format(person):
    return ("Mr. " if person[3] == "M" else "Ms. ") + person[0] + " " + person[1]


if __name__ == '__main__':
    people = [raw_input().split() for i in range(int(raw_input()))]
    print '\n'.join(name_format(people))