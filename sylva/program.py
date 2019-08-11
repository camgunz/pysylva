from . import sylva
from .data_source import DataSource
from .module import Module
from .module_loader import ModuleLoader


class Program:

    def __init__(self, data_sources):
        self.modules = {
            module.name: module
            for module in ModuleLoader.load_from_data_sources(
                self,
                data_sources
            )
        }
        self._build_builtin_modules()
        for module in self.modules.values():
            module.resolve_dependencies([])

    def _build_builtin_modules(self):
        self.modules['sys'] = Module.BuiltIn(self, 'sys')

    @property
    def is_executable(self):
        return sylva.MAIN_MODULE_NAME in self.modules

    def parse(self):
        for module in self.modules.values():
            module.parse()

    def get_module(self, name):
        try:
            return self.modules[name]
        except KeyError:
            return None

    def get_main_module(self):
        return self.get_module(sylva.MAIN_MODULE_NAME)

    def get_default_module(self):
        return self.get_main_module()
