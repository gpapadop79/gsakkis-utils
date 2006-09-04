def bin(n):
    s = []
    def bin(n):
         if n == 0:
             yield s
         else:
             s.append(0)
             for s1 in bin(n - 1):
                 yield s1
             s.pop()
             s.append(1)
             for s1 in bin(n - 1):
                 yield s1
             s.pop()
    return bin(n)

def bin2(n):
    if n:
        for tail in bin2(n-1):
            yield [0] + tail
            yield [1] + tail
    else:
        yield []


def bin3(n):
    array = [None]*n
    x=[n]
    def _bin():
        if not x[0]:
            yield array
        else:
            x[0] -= 1
            n = x[0]
            for perm in _bin():
                perm[n] = 0; yield perm
                perm[n] = 1; yield perm
    return _bin()

