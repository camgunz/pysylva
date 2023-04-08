from dataclasses import dataclass

from sylva.builtins import NamedSylvaObject


@dataclass(kw_only=True, slots=True)
class Req(NamedSylvaObject):
    bound_name: str | None = None
