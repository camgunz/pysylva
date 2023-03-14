from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sylva.mod import Mod

from sylva.location import Location


@dataclass(kw_only=True, slots=True)
class Req:
    location: Location
    name: str
    module: 'Mod'
    bound_name: Optional[str] = None
