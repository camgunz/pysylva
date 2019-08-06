from . import errors


class DataSource:

    __slots__ = ('name', 'data', 'begin', 'end')

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.begin = 0
        self.end = len(self.data) - 1

    @classmethod
    def Raw(cls, data):
        return cls('<data>', data)

    @classmethod
    def FromFile(cls, file_path):
        with open(file_path, 'r', encoding='UTF-8') as fobj:
            return cls(file_path, fobj.read())

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return 'DataSource(%r)' % (self.name)

    def copy(self):
        return DataSource(self.name, self.data)

    def at(self, location):
        if location.index < self.begin or location.index > self.end:
            raise IndexError('Data index out of range')
        return self.data[location.index:]

    def set_begin(self, location):
        if location.index >= len(self.data):
            raise IndexError('Data index out of range')
        self.begin = location.index

    def set_end(self, location):
        if location.index >= len(self.data):
            raise IndexError('Data index out of range')
        self.end = location.index

