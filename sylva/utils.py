from collections import defaultdict


def strlist(elements, flat=False, conjunction='or'):
    if len(elements) == 1:
        return elements[0]
    elements = [str(element) for element in elements]
    if flat:
        return ', '.join(elements)
    return f', {conjunction} '.join([', '.join(elements[:-1]), elements[-1]])


def get_dupes(strs):
    counts = defaultdict(lambda: 0)
    for s in strs:
        counts[s] += 1
    return [s for s, count in counts.items() if count > 1]
