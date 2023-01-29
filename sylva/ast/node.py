from dataclasses import dataclass, field
from typing import Optional

from sylva.location import Location


@dataclass(kw_only=True)
class Node:
    name: Optional[str] = None
    location: Location = field(default_factory=Location.Generate)

    @property
    def is_anonymous(self):
        return self.name is None
