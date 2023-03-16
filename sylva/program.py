from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import lark

from cdump.parser import Parser as CParser  # type: ignore

from sylva import errors, sylva
from sylva.ast_builder import ASTBuilder
from sylva.mod import Mod
from sylva.package_loader import PackageLoader
from sylva.package import BasePackage, SylvaPackage, get_package_from_path
from sylva.parser import Parser
from sylva.scope_gatherer import ScopeGatherer


@dataclass(kw_only=True, slots=True)
class Program:
    package: SylvaPackage
    deps_folder: Path
    stdlib: Path
    c_preprocessor: Path
    libclang: Path
    c_parser: CParser = field(init=False)
    modules: list[Mod] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.package, SylvaPackage):
            raise errors.InvalidMainPackageType(
                self.package_file, self.package.type
            )
        self.c_parser = CParser(self.c_preprocessor, self.libclang)

        self.modules = PackageLoader(self).load_package(self.package)

    def parse(self):
        parser = Parser()
        scope_gatherer = ScopeGatherer()

        module_trees = [ # yapf: ignore
            (module, location, parser.parse(location.stream.data))
            for module in self.modules.values()
            for location in module.locations
        ]

        for module, location, tree in module_trees:
            scope_gatherer.visit_topdown(tree)

        module_trees = [ # yapf: ignore
            (
                module,
                location,
                ASTBuilder( # yapf: ignore
                    program=self,
                    module=module,
                    location=location
                ).transform(tree)
            )
            for module, location, tree in module_trees
        ]

        return lark.Tree(data='Program', children=module_trees)

    def compile(self, output_folder):
        raise NotImplementedError

    def get_module(self, name):
        return self.modules.get(name)

    @property
    def is_executable(self):
        return sylva.MAIN_MODULE_NAME in self.modules

    @property
    def main_module(self):
        return self.get_module(sylva.MAIN_MODULE_NAME)

    @property
    def default_module(self):
        return self.main_module

    def get_package(self, req_name) -> Optional[BasePackage]:
        package_name = req_name.split('.')[0]
        path = ( # yapf: ignore
            self.stdlib if package_name == 'std'
            else self.deps_folder / package_name
        ) / 'package.toml'
        return get_package_from_path(path) if path.is_file() else None
