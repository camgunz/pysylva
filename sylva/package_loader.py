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
        location = Location.FromTree(tree, stream=self._stream)
        name = '.'.join(t.value for t in tree.children[1:-1])
        bound_name = tree.children[-1].value if tree.children[-1] else None
        module = self._package_loader.resolve_requirement(
            self._current_module, location, name
        )

        req = Req(
            location=location, name=name, bound_name=bound_name, module=module
        )

        # [NOTE] Should we disallow duplicate requirements here?
        self._current_module.requirements[  # yapf: ignore
            req.bound_name if req.bound_name else req.name  # yapf: ignore
        ] = req


@dataclass
class PackageLoader:
    program: 'Program'
    missing: set[Location] = field(default_factory=set, init=False)
    modules: dict[str, Mod] = field(default_factory=dict, init=False)
    _parser: lark.lark.Lark = field(default_factory=Parser, init=False)

    def process_c_lib_package(self, package: CLibPackage):
        loader = CModuleLoader(program=self.program)
        c_lib_modules = loader.load_package(package)
        self.modules.update(**c_lib_modules)

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

    def resolve_requirement(self, module: Mod, location: Location, name: str):
        resolved_module = self.modules.get(name)
        if resolved_module:
            return resolved_module

        package = self.program.get_package(name)

        if not package:
            self.missing.add(location)
            return

        # If the req is in the same package as this, that means files are
        # specified out of order
        if package == module.package:
            raise errors.OutOfOrderPackageModules(
                location=location,
                package_name=package.name,
                module_name=module.name,
                name=name,
            )

        if isinstance(package, CLibPackage):
            self.process_c_lib_package(package)
        elif isinstance(package, SylvaPackage):
            self.process_sylva_package(package)

        resolved_module = self.modules.get(name)
        if not resolved_module:
            self.missing.add(location)

        return resolved_module

    def load_package(self, package: SylvaPackage):
        if package.name in self.modules:
            return {}

        self.process_sylva_package(
            self.program.get_package('std')  # type: ignore
        )

        self.process_sylva_package(package)

        if self.missing:
            raise errors.MissingRequirements(self.missing)

        ts: TopologicalSorter = TopologicalSorter()

        for n, m in self.modules.items():
            ts.add(n, *[r.name for r in m.requirements.values()])

        try:
            ordered_module_names = ts.static_order()
        except CycleError as e:
            raise errors.CyclicRequirements(e.args[1])

        return [self.modules[n] for n in ordered_module_names]
