import math

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


def round_up_to_power_of_two(x, start=8):
    exp = int(math.log(start, 2))

    if exp != math.log(start, 2):
        raise ValueError(f'{start} is not a power of 2')

    val = exp ** 2

    while val < x:
        exp += 1
        val = exp ** 2

    return val


def len_prefix(s):
    return f'{len(s)}{s}'


def mangle(seq):
    return ''.join(len_prefix(s) for s in map(str, seq))


def demangle(s):
    length = []
    tokens = []
    seq = list(s)
    while seq:
        if not seq[0].isdigit():
            tlen = int(''.join(length))
            tokens.append(seq[:tlen])
            seq = seq[tlen:]
            length = []
        else:
            length.append(seq.pop(0))
    return tokens
