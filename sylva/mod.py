from dataclasses import dataclass, field
from enum import Enum
from typing import Union

from sylva import builtins, errors
from sylva.builtins import (
    SylvaDef,
    SylvaObject,
    SylvaType,
    SylvaValue,
    TypeDef,
)
from sylva.location import Location
from sylva.package import BasePackage
from sylva.req import Req


@dataclass(kw_only=True)
class ModDecl(SylvaObject):
    name: str


@dataclass(kw_only=True, slots=True)
class Mod:
    class Type(Enum):
        Sylva = 'sylva'
        C = 'c'

    name: str
    package: BasePackage
    type: Type = Type.Sylva
    locations: list[Location] = field(default_factory=list)
    requirements: dict[str, Req] = field(default_factory=dict)
    defs: dict[str, Union[SylvaDef, TypeDef]] = field(
        init=False, default_factory=dict
    )

    def add_def(self, d: Union[SylvaDef, TypeDef]):
        if preexisting := builtins.lookup(d.name):
            raise errors.RedefinedBuiltIn(d.location, d.name) # type: ignore

        if preexisting := self.defs.get(d.name):
            raise errors.DuplicateDefinition(
                d.name, d.location, preexisting.location
            )

        if preexisting := self.requirements.get(d.name):
            raise errors.DuplicateDefinition(
                d.name, d.location, preexisting.location
            )

        self.defs[d.name] = d

    def lookup(self, name) -> Union['Mod', SylvaValue, SylvaType]:
        res = self.defs.get(name)
        if res is not None:
            match res:
                case SylvaDef():
                    return res.value
                case TypeDef():
                    return res.type
                case _:
                    breakpoint()

        if req := self.requirements.get(name):
            return req.module

        return builtins.lookup(name)
