from . import sylva
from .codegen import CodeGen
from .compiler import Compiler
from .module_loader import ModuleLoader
from .stdlib import Stdlib


class Program:

    def __init__(self, data_sources, stdlib_path=None, target_triple=None):
        self.stdlib = Stdlib.FromPath(stdlib_path or 'stdlib')
        self.stdlib_modules = {
            module.name: module
            for module in ModuleLoader.load_from_data_sources(
                self,
                self.stdlib.data_sources
            )
        }

        unordered_modules = {
            module.name: module
            for module in ModuleLoader.load_from_data_sources(
                self,
                data_sources
            )
        }

        # [TODO] Do some kind of searching
        self.stdlib_path = stdlib_path

        for module in unordered_modules.values():
            module.resolve_requirements([])

        ordered_modules = []
        for module in unordered_modules.values():
            self.order_module(module, ordered_modules)

        self.modules = {module.name: module for module in ordered_modules}

        self.compiler = Compiler(target_triple)

    def order_module(self, module, modules):
        if module in modules:
            return
        for req in module.requirements:
            self.order_module(req, modules)
        modules.append(module)

    @property
    def is_executable(self):
        return sylva.MAIN_MODULE_NAME in self.modules

    def parse(self):
        for module in self.modules.values():
            module.parse()

    def compile(self, output_folder):
        # [TODO] Something about name and output folder...?
        compiler = Compiler()
        for module in self.modules.values():
            compiler.compile_ir_to_file(
                module.get_ir(),
                output_folder / module.name
            )

    def get_module(self, name):
        try:
            return self.stdlib_modules[name]
        except KeyError:
            pass

        try:
            return self.modules[name]
        except KeyError:
            pass

    def get_main_module(self):
        return self.get_module(sylva.MAIN_MODULE_NAME)

    def get_default_module(self):
        return self.get_main_module()
