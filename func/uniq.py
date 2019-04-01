def uniq_sign(a=list):
    one_val = set(a)
    uniq = []
    for item in one_val:
        if a.count(item) == 1:
           uniq.append(item)
    return uniq

print(uniq_sign([1, 3, 4,-1, 1, 3, 4, 5]))
print(uniq_sign([0, 0 , 1, 1]))
print(uniq_sign([]))