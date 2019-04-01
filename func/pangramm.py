def pangramm(line = ''):

    import string
    abc = string.ascii_lowercase

    for item in abc:
        if item not in line:
            return False
    return True

print(pangramm('hello'))
print(pangramm('qwertyuiopasdfghjklzxcvbnm'))
print(pangramm())