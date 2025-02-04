from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import lark

from cdump.parser import Parser as CParser  # type: ignore

from sylva import errors
from sylva.ast_builder import ASTBuilder
from sylva.builtins import FnValue
from sylva.c_code_gen import CCodeGen
from sylva.lookup_expr_type_assigner import LookupExprTypeAssigner
from sylva.mod import Mod
from sylva.monomorphizer import Monomorphizer
from sylva.package_loader import PackageLoader
from sylva.package import BasePackage, SylvaPackage, get_package_from_path
from sylva.parser import Parser
from sylva.scope_gatherer import ScopeGatherer
from sylva.type_checker import TypeChecker


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
            for module in self.modules
            for location in module.locations
        ]

        try:
            for _, __, tree in module_trees:
                scope_gatherer.visit_topdown(tree)
        except lark.exceptions.VisitError as ve:
            raise ve.orig_exc from None

        try:
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
        except lark.exceptions.VisitError as ve:
            raise ve.orig_exc from None

        return lark.Tree(data='Program', children=module_trees)

    def process(self):
        self.parse()
        type_assigner = LookupExprTypeAssigner()
        monomorphizer = Monomorphizer()
        type_checker = TypeChecker()
        for m in self.modules:
            if m.type == m.Type.C:
                continue
            type_assigner.visit(m)
            monomorphizer.visit(m)
            type_checker.visit(m)

    def compile(self, output_folder: Path):
        self.process()
        c_code_generator = CCodeGen()
        for m in self.modules:
            if m.type == m.Type.C:
                continue
            p = output_folder / (m.name + '.c')
            c_code = c_code_generator.visit(m)
            print(f'{m.name} ---\n{c_code}')
            p.write_text(c_code)

    @property
    def is_executable(self):
        return bool(self.main_func)

    @cached_property
    def main_module(self):
        for m in self.modules:
            if m.is_main:
                return m

    @property
    def main_func(self):
        if (main_module := self.main_module) is None:
            return False
        if (main := main_module.lookup('main')) is None:
            return False
        return main if isinstance(main, FnValue) else None

    @property
    def default_module(self):
        return self.main_module

    def get_package(self, req_name) -> BasePackage | None:
        package_name = req_name.split('.')[0]
        path = ( # yapf: ignore
            self.stdlib if package_name == 'std'
            else self.deps_folder / package_name
        ) / 'package.toml'
        return get_package_from_path(path) if path.is_file() else None
