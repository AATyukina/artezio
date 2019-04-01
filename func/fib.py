def fib(n, a=[0, 1]):
    if n <= 0:
        return Exception("Incorrect index " + str(n))
    if len(a)==n:
        return a[n-1]
    else:
        a.append(a[len(a)-1]+a[len(a)-2])
        return fib(n, a)

print(fib(5))
print(fib(-2))