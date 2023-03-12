from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True, slots=True, frozen=True)
class Stream:
    name: str
    data: str

    @classmethod
    def FromPath(cls, path: Path):
        return cls(name=str(path), data=path.read_text(encoding='utf-8'))
