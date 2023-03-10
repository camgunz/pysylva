from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True, slots=True, frozen=True)
class Stream:
    name: str
    data: str

    @classmethod
    def FromPath(cls, file_path: Path):
        return cls(
            name=str(file_path), data=file_path.read_text(encoding='utf-8')
        )
