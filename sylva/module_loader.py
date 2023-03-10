from dataclasses import dataclass, field
from functools import cache
from graphlib import CycleError, TopologicalSorter
from pathlib import Path

import lark

from sylva import debug, errors
from sylva.location import Location
from sylva.mod import Mod
from sylva.parser import Parser
from sylva.req import Req
from sylva.stream import Stream


@cache
def get_def_file_path(deps_folder, req_name):
    def_file = deps_folder / req_name / 'defs.sy'
    if def_file.is_file():
        return def_file


class ModuleGatherer(lark.Visitor):

    def __init__(self, stream, mod_loader):
        self._stream = stream
        self._mod_loader = mod_loader
        self._current_module = None

    def module_decl(self, tree):
        debug('ast_builder', f'module_decl: {tree}')
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
        debug('ast_builder', f'requirement_decl: {tree}')

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
class ModuleLoader:
    deps_folder: Path
    missing: set[Req] = field(default_factory=set, init=False)
    modules: dict[str, Mod] = field(default_factory=dict, init=False)
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
            mod = Mod(name=mod_name, locations=[loc])
            self.modules[mod_name] = mod
        else:
            mod = self.modules[mod_name]
            mod.locations.append(loc)

        return mod

    def resolve_requirement(self, req):
        if self.modules.get(req.name):
            return

        def_file_path = get_def_file_path(self.deps_folder, req.name)

        if not def_file_path:
            self.missing.add(req)
            return

        self.process_stream(Stream.FromPath(def_file_path))

    def load_streams(self, streams):
        for s in streams:
            self.process_stream(s)

        if self.missing:
            raise errors.MissingRequirements(self.missing)

        ts = TopologicalSorter()

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
