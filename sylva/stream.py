from attrs import define


@define(frozen=True, slots=True)
class Stream:
    name: str
    data: str

    @classmethod
    def FromFile(cls, file_path, encoding='utf-8'):
        with open(file_path, 'r', encoding=encoding) as fobj:
            return cls(file_path, fobj.read())

    def __str__(self):
        return f'<Stream {self.name}>'

    def __repr__(self):
        return f'Stream({self.name})'
