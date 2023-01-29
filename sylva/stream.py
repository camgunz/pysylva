from dataclasses import dataclass


@dataclass(kw_only=True, slots=True, frozen=True)
class Stream:
    name: str
    data: str

    @classmethod
    def FromFile(cls, file_path, encoding='utf-8'):
        with open(file_path, 'r', encoding=encoding) as fobj:
            return cls(name=file_path, data=fobj.read())
