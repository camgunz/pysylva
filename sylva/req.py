from dataclasses import dataclass
from typing import Optional

from sylva.location import Location


@dataclass(kw_only=True, frozen=True, slots=True)
class Req:
    location: Location
    name: str
    bound_name: Optional[str] = None
