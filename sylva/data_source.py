from sylva import debug


class DataSource:

    __slots__ = ('name', 'data', 'begin', 'end')

    def __init__(self, name, data, begin=0, end=None):
        self.name = name
        self.data = data
        self.begin = begin
        self.end = end or len(self.data) - 1
        debug([self.name, self.begin, self.end])

    @classmethod
    def Raw(cls, data):
        return cls('<data>', data)

    @classmethod
    def FromFile(cls, file_path):
        with open(file_path, 'r', encoding='UTF-8') as fobj:
            return cls(file_path, fobj.read())

    @classmethod
    def FromPath(cls, path):
        return cls(path.name, path.read_text(encoding='utf-8'))

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
        debug(f'set_begin: {self.name} {location}')
        if location.index >= len(self.data):
            raise IndexError('Data index out of range')
        self.begin = location.index

    def set_end(self, location):
        debug(f'set_end: {self.name} {location}')
        if location.index >= len(self.data):
            raise IndexError('Data index out of range')
        self.end = location.index
