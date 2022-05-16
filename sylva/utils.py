from collections import defaultdict


def strlist(elements, flat=False, conjunction='or'):
    if not hasattr(elements, '__iter__'):
        return str(elements)

    elements = list(map(str, elements))

    if len(elements) == 1:
        return elements[0]

    if flat:
        return ', '.join(elements)

    return f', {conjunction} '.join([', '.join(elements[:-1]), elements[-1]])


def get_dupes(strs):
    counts = defaultdict(lambda: 0)
    for s in strs:
        counts[s] += 1
    return [s for s, count in counts.items() if count > 1]


def smallest_uint(x):
    assert x >= 0, 'x must be unsigned'
    bits = 0
    while x:
        x >>= 8
        bits += 8
    return bits


def round_up_to_multiple(x, base):
    rem = x % base
    if rem == 0:
        return x
    return x + base - rem
