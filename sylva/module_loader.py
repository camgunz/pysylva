from dataclasses import dataclass, field
from functools import cache
from graphlib import CycleError, TopologicalSorter
from os.path import sep as PATH_SEP
from pathlib import Path

import lark

from sylva import errors
from sylva.location import Location
from sylva.parser import Parser
from sylva.stream import Stream


@dataclass(kw_only=True, frozen=True, slots=True)
class Requirement:
    name: str
    location: Location


@dataclass(kw_only=True, slots=True)
class Module:
    name: str
    locations: list[Location] = field(default_factory=list)
    requirements: list[Requirement] = field(default_factory=list)


@cache
def get_requirement_path(search_paths, req_name):
    req_file = f'{req_name.replace(".", PATH_SEP)}.sy'
    for search_path in search_paths:
        req_path = (search_path / req_file).absolute()
        if req_path.is_file():
            return req_path


class ModuleGatherer(lark.Visitor):

    def __init__(self, stream, mod_tracker):
        self._stream = stream
        self._mod_tracker = mod_tracker
        self._current_module = None

    def module_decl(self, tree):
        mod_name = tree.children[0].value
        loc = Location.FromTree(tree, stream=self._stream)

        mod = self._mod_tracker.upsert_module_from_location(mod_name, loc)
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
        req = Requirement(
            location=Location.FromTree(tree, stream=self._stream),
            name=tree.children[0].value
        )

        if req.name not in [r.name for r in self._current_module.requirements]:
            self._current_module.requirements.append(req)

        self._mod_tracker.resolve_requirement(req)


@dataclass
class ModuleLoader:
    search_paths: frozenset[Path]
    missing: set[Requirement] = field(default_factory=set, init=False)
    modules: dict[str, Module] = field(default_factory=dict, init=False)
    _parser: lark.lark.Lark = field(default_factory=Parser, init=False)

    def process_stream(self, stream):
        try:
            ModuleGatherer(stream, self).visit(self._parser.parse(stream.data))
        except lark.UnexpectedToken as e:
            raise errors.UnexpectedToken(
                Location.FromUnexpectedTokenError(e, stream=stream),
                e.token.value,
                e.expected
            ) from None

    def upsert_module_from_location(self, mod_name, loc):
        if mod_name not in self.modules:
            mod = Module(name=mod_name, locations=[loc])
            self.modules[mod_name] = mod
        else:
            mod = self.modules[mod_name]
            mod.locations.append(loc)

        return mod

    def resolve_requirement(self, req):
        mod = self.modules.get(req.name)
        if mod:
            return

        req_path = get_requirement_path(self.search_paths, req.name)

        if not req_path:
            self.missing.add(req)
            return

        self.process_stream(Stream.FromFile(str(req_path)))

    def load_streams(self, streams):
        for s in streams:
            self.process_stream(s)

        if self.missing:
            raise errors.MissingRequirements(self.missing)

        ts = TopologicalSorter()

        for n, m in self.modules.items():
            ts.add(n, *[req.name for req in m.requirements])

        try:
            ordered_module_names = ts.static_order()
        except CycleError as e:
            raise errors.CyclicRequirements(e.args[1])

        return {
            m.name: m
            for m in [self.modules[n] for n in ordered_module_names]
        }
