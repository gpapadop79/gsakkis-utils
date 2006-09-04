def len_(iterable):
    import __builtin__
    try: return __builtin__.len(iterable)
    except TypeError:
        count = 0
        for i in iterable: count+=1
        return count

def normalize(seq, minimum=0.0, maximum=1.0):
    base = min(seq)
    range = max(seq)-base
    new_range = maximum - minimum
    return [minimum + float(i-base)/range*new_range for i in seq]


def num2str(num):
    '''Return a string representation of a number with the thousands being
    delimited.

    >>> num2str(65837)
    '65,837'
    >>> num2str(6582942)
    '6,582,942'
    >>> num2str(23)
    '23'
    >>> num2str(-1934)
    '-1,934'
    '''
    parts = []
    div = abs(num)
    while True:
        div,mod = divmod(div,1000)
        parts.append(mod)
        if not div:
            if num < 0: parts[-1] *= -1
            return ','.join(str(part) for part in reversed(parts))


