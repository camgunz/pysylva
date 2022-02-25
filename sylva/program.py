from . import sylva
# from .module import Module
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

        self.modules = {
            module.name: module
            for module in ModuleLoader.load_from_data_sources(
                self,
                data_sources
            )
        }
        # [TODO] Do some kind of searching
        self.stdlib_path = stdlib_path
        # self._build_builtin_modules()
        for module in self.modules.values():
            module.resolve_requirements([])

        self.compiler = Compiler(target_triple)

    # def _build_builtin_modules(self):
    #     self.modules['sys'] = Module.BuiltIn(self, 'sys')

    @property
    def is_executable(self):
        return sylva.MAIN_MODULE_NAME in self.modules

    def parse(self):
        for module in self.modules.values():
            module.parse()

    def compile(self):
        # [TODO]
        self.parse()

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
