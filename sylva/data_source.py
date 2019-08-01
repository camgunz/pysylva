from . import errors


class DataSource:

    def __init__(self, name, data):
        self.name = name
        self.data = data

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

    def at(self, index):
        if index >= len(self.data):
            raise errors.EOF()
        return self.data[index:]
