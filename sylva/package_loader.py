import shutil

from dataclasses import dataclass, field
from graphlib import CycleError, TopologicalSorter
from typing import TYPE_CHECKING

import lark

from sylva import debug, errors
from sylva.cffi import CModuleLoader
from sylva.location import Location
from sylva.mod import Mod
from sylva.package import CLibPackage, SylvaPackage
from sylva.parser import Parser
from sylva.req import Req
from sylva.stream import Stream

if TYPE_CHECKING:
    from sylva.program import Program


class ModuleGatherer(lark.Visitor):

    def __init__(self, stream, package_loader, package):
        self._stream = stream
        self._package_loader = package_loader
        self._package = package
        self._current_module = None

    def module_decl(self, tree):
        debug('module_gatherer', f'module_decl: {tree}')
        mod_name = '.'.join(t.value for t in tree.children[1:])
        loc = Location.FromTree(tree, stream=self._stream)

        mod = self._package_loader.upsert_module(mod_name, self._package, loc)
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

        self._package_loader.resolve_requirement(self._current_module, req)


@dataclass
class PackageLoader:
    program: 'Program'
    missing: set[Req] = field(default_factory=set, init=False)
    modules: dict[str, Mod] = field(default_factory=dict, init=False)
    _parser: lark.lark.Lark = field(default_factory=Parser, init=False)

    def process_c_lib_package(self, package: CLibPackage):
        loader = CModuleLoader(program=self.program)
        self.modules.update(**loader.load_package(package))

    def process_sylva_package(self, package: SylvaPackage):
        for dep in package.dependencies:
            dest = self.program.deps_folder / dep.name
            try:
                shutil.copytree(dep.location, dest)
            except FileExistsError:
                continue

        for stream in package.get_streams():
            gatherer = ModuleGatherer(stream, self, package)
            try:
                gatherer.visit(self._parser.parse(stream.data))
            except lark.UnexpectedToken as e:
                raise
                raise errors.UnexpectedToken(
                    Location.FromLarkError(e, stream=stream),
                    e.token.value,
                    e.expected
                ) from None
            except lark.UnexpectedCharacters as e:
                raise errors.UnexpectedCharacter(
                    Location.FromLarkError(e, stream=stream),
                    e.char,
                    e.allowed,
                )

    def upsert_module(self, mod_name, package, loc):
        mod = self.modules.get(mod_name)
        if mod is None:
            mod = Mod(name=mod_name, package=package, locations=[loc])
            self.modules[mod_name] = mod
        else:
            mod.locations.append(loc)

        return mod

    def resolve_requirement(self, module: Mod, req: Req):
        if self.modules.get(req.name):
            return

        package = self.program.get_package(req.name)

        if not package:
            print(f'Missing package {req.name}')
            self.missing.add(req)
            return

        # If the req is in the same package as this, that means files are
        # specified out of order
        if package == module.package:
            raise errors.OutOfOrderPackageModules(
                package_name=package.name,
                module_name=module.name,
                req=req,
            )

        if isinstance(package, CLibPackage):
            self.process_c_lib_package(package)
        elif isinstance(package, SylvaPackage):
            self.process_sylva_package(package)

    def load_package(self, package: SylvaPackage):
        self.process_sylva_package(
            self.program.get_package('std')  # type: ignore
        )

        self.process_sylva_package(package)

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
