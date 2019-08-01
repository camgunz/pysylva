def strlist(elements, flat=False):
    if len(elements) == 1:
        return elements[0]
    elements = [str(element) for element in elements]
    if flat:
        return ', '.join(elements)
    return ', or '.join([', '.join(elements[:-1]), elements[-1]])
