from dataclasses import dataclass, field
from functools import cache
from graphlib import CycleError, TopologicalSorter
from typing import Optional, TYPE_CHECKING

import lark

from sylva import debug, errors
from sylva.location import Location
from sylva.mod import Mod
from sylva.package import BasePackage, SylvaPackage, get_package_from_path
from sylva.parser import Parser
from sylva.req import Req
from sylva.stream import Stream

if TYPE_CHECKING:
    from sylva.program import Program


class ModuleGatherer(lark.Visitor):

    def __init__(self, stream, mod_loader):
        self._stream = stream
        self._mod_loader = mod_loader
        self._current_module = None

    def module_decl(self, tree):
        debug('module_gatherer', f'module_decl: {tree}')
        mod_name = '.'.join(t.value for t in tree.children[1:])
        loc = Location.FromTree(tree, stream=self._stream)

        mod = self._mod_loader.upsert_module_from_location(mod_name, loc)
        pmod = self._current_module
        self._current_module = mod

        if not pmod:
            return

        ploc = mod.locations[-2] if mod == pmod else pmod.locations[-1]
        loc = mod.locations[-1]

        ploc.stream = Stream(
            name=ploc.stream_name,
            data=ploc.stream.data[ploc.index:loc.index] + '\n'
        )

    def requirement_decl(self, tree):
        debug('module_gatherer', f'requirement_decl: {tree}')

        req = Req(
            location=Location.FromTree(tree, stream=self._stream),
            name='.'.join(t.value for t in tree.children[1:-1])
        )

        # [NOTE] Should we disallow duplicate requirements here?
        self._current_module.requirements[  # yapf: ignore
            req.bound_name if req.bound_name else req.name  # yapf: ignore
        ] = req

        self._mod_loader.resolve_requirement(req)


@dataclass
class PackageLoader:
    program: 'Program'
    missing: set[Req] = field(default_factory=set, init=False)
    modules: dict[str, Mod] = field(default_factory=dict, init=False)
    _parser: lark.lark.Lark = field(default_factory=Parser, init=False)

    def process_package(self, package):
        for stream in package.get_streams():
            gatherer = ModuleGatherer(stream, self)
            try:
                gatherer.visit(self._parser.parse(stream.data))
            except lark.UnexpectedToken as e:
                raise errors.UnexpectedToken(
                    Location.FromUnexpectedTokenError(e, stream=stream),
                    e.token.value,
                    e.expected
                ) from None

    def upsert_module_from_location(self, mod_name, loc):
        mod = self.modules.get(mod_name)
        if mod is None:
            mod = Mod(name=mod_name, locations=[loc])
            self.modules[mod_name] = mod
        else:
            mod.locations.append(loc)

        return mod

    def resolve_requirement(self, req):
        if self.modules.get(req.name):
            return

        package = self.program.get_package(req.name)

        if not package:
            self.missing.add(req)
            return

        self.process_package(package)

    def load_package(self, package: SylvaPackage):
        self.process_package(self.program.get_package('std'))

        self.process_package(package)

        if self.missing:
            raise errors.MissingRequirements(self.missing)

        ts: TopologicalSorter = TopologicalSorter()

        for n, m in self.modules.items():
            ts.add(n, *list(m.requirements.keys()))

        try:
            ordered_module_names = ts.static_order()
        except CycleError as e:
            raise errors.CyclicRequirements(e.args[1])

        return {
            m.name: m
            for m in [self.modules[n] for n in ordered_module_names]
        }
