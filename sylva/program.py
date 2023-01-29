from os.path import sep as PATH_SEP
from functools import cache
from graphlib import CycleError, TopologicalSorter

import lark
import llvmlite # type: ignore

from sylva import errors, sylva, target
from sylva.ast_builder import ASTBuilder
from sylva.module_loader import ModuleLoader
from sylva.parser import Parser


class Program:

    def __init__(self, streams, search_paths, target_triple=None):
        target.make_target(target_triple=target_triple)

        self._search_paths = search_paths
        self._required_modules = []

        modules = { # yapf: ignore
            **ModuleLoader.load_from_streams(self, streams),
            **{m.name: m for m in self._required_modules}
        }

        ts = TopologicalSorter()
        for n, m in modules.items():
            ts.add(n, *[req.name for req in m.requirements])

        try:
            ordered_module_names = list(ts.static_order())
        except CycleError as e:
            raise errors.CyclicRequirements(e.args[1])

        self.modules = {
            m.name: m
            for m in [modules[n] for n in ordered_module_names]
        }

    def parse(self):
        parser = Parser()

        module_trees = [
            ASTBuilder(location=loc).transform(parser.parse(loc.stream.data))
            for module in self.modules.values()
            for loc in module.locations
        ]

        return lark.Tree( # yapf: disable
            data='Program',
            children=module_trees
        )

    def compile(self, output_folder):
        compile_errors = []
        for module in self.modules.values():
            parse_errors = module.parse()
            if parse_errors:
                compile_errors.extend(parse_errors)
            else:
                try:
                    llvm_module = module.emit(module=module)
                except errors.SylvaError as se:
                    compile_errors.append(se)
                else:
                    llvm_mod_ref = (
                        llvmlite.binding.parse_assembly(str(llvm_module))
                    )
                    llvm_mod_ref.verify()
                    object_code = (
                        target.get_target().machine.emit_object(llvm_mod_ref)
                    )
                    with open(output_folder / module.name, 'wb') as fobj:
                        fobj.write(object_code)
        return errors

    def register_required_module(self, module):
        if module.name not in [m.name for m in self._required_modules]:
            self._required_modules.append(module)

    def get_module(self, name):
        return self.modules.get(name)

    @cache
    def get_requirement_path(self, name):
        req_file = f'{name.replace(".", PATH_SEP)}.sy'
        for search_path in self._search_paths:
            req_path = (search_path / req_file).absolute()
            if req_path.is_file():
                return req_path

    @property
    def is_executable(self):
        return sylva.MAIN_MODULE_NAME in self.modules

    @property
    def main_module(self):
        return self.get_module(sylva.MAIN_MODULE_NAME)

    @property
    def default_module(self):
        return self.main_module
