from dataclasses import dataclass, field
from typing import Union

from sylva import builtins, errors
from sylva.builtins import SylvaDef, SylvaObject, TypeDef
from sylva.location import Location
from sylva.req import Req


@dataclass(kw_only=True)
class ModDecl(SylvaObject):
    name: str


@dataclass(kw_only=True, slots=True)
class Mod:
    locations: list[Location] = field(default_factory=list)
    name: str
    requirements: list[Req] = field(default_factory=list)
    type_defs: dict[str, TypeDef] = field(init=False, default_factory=dict)
    defs: dict[str, SylvaDef] = field(init=False, default_factory=dict)

    def add_def(self, d: Union[SylvaDef, TypeDef]):
        if preexisting := self.lookup(d.name):
            raise errors.DuplicateDefinition(
                d.loc, d.name, preexisting.location
            )

        (self.defs if isinstance(d, SylvaDef) else self.type_defs)[d.name] = d

    def lookup(self, name):
        return self.type_defs.get(
            name, self.defs.get(name, builtins.lookup(name))
        )
