from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from queue import SimpleQueue
from typing import Union

from sylva import builtins, errors, sylva
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
    package: BasePackage = field(repr=False)
    type: Type = Type.Sylva
    locations: list[Location] = field(default_factory=list, repr=False)
    requirements: dict[str, Req] = field(default_factory=dict, repr=False)
    defs: dict[str, SylvaDef | TypeDef] = field(
        init=False, default_factory=dict, repr=False
    )
    _def_queues: list[SimpleQueue] = field(repr=False, default_factory=list)

    @property
    def is_main(self):
        return self.name == sylva.MAIN_MODULE_NAME

    @contextmanager
    def def_listener(self):
        i = len(self._def_queues)
        q = SimpleQueue()
        for d in self.defs.values():
            q.put(d)
        self._def_queues.append(q)
        yield q
        self._def_queues.pop(i)

    def _check_def(self, d: SylvaDef |  TypeDef):
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

    def add_def(self, d: SylvaDef |  TypeDef):
        self._check_def(d)

        self.defs[d.name] = d

        for q in self._def_queues:
            q.put(d)

    def insert_def(self, d: SylvaDef | TypeDef, before: str):
        self._check_def(d)

        new_defs = {}

        found = False

        for n, ed in self.defs.items():
            if n == before:
                new_defs[d.name] = d
                found = True
            new_defs[n] = ed

        if found:
            self.defs = new_defs
        else:
            self.defs[d.name] = d

        for q in self._def_queues:
            q.put(d)

    def lookup(self, name) -> Union['Mod', SylvaValue, SylvaType]:
        res = self.defs.get(name)
        if res is not None:
            match res:
                case SylvaDef():
                    return res.value
                case TypeDef():
                    return res.type

        if req := self.requirements.get(name):
            return req.module

        return builtins.lookup(name)
