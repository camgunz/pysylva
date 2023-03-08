from dataclasses import dataclass, field
from typing import Union

from sylva import builtins, errors
from sylva.builtins import SylvaDef, SylvaObject, TypeDef
from sylva.const import ConstDef
from sylva.location import Location
from sylva.req import Req


@dataclass(kw_only=True)
class ModDecl(SylvaObject):
    name: str


@dataclass(kw_only=True, slots=True)
class Mod:
    locations: list[Location] = field(default_factory=list)
    name: str
    requirements: dict[str, Req] = field(default_factory=dict)
    type_defs: dict[str, TypeDef] = field(init=False, default_factory=dict)
    defs: dict[str, Union[ConstDef, SylvaDef]] = field(
        init=False, default_factory=dict
    )

    def add_def(self, d: Union[ConstDef, SylvaDef, TypeDef]):
        if preexisting := builtins.lookup(d.name):
            raise errors.RedefinedBuiltIn(d.location, d.name)

        if preexisting := self.type_defs.get(d.name):
            raise errors.DuplicateDefinition(
                d.location, d.name, preexisting.location
            )

        if preexisting := self.defs.get(d.name):
            raise errors.DuplicateDefinition(
                d.location, d.name, preexisting.location
            )

        if preexisting := self.requirements.get(d.name):
            raise errors.DuplicateDefinition(
                d.location, d.name, preexisting.location
            )

        if isinstance(d, (ConstDef, SylvaDef)):
            self.defs[d.name] = d
        elif isinstance(d, TypeDef):
            self.type_defs[d.name] = d

    def lookup(self, name):
        return self.type_defs.get(
            name,
            self.defs.get(
                name, self.requirements.get(name, builtins.lookup(name))
            )
        )
