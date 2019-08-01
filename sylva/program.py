from .module import Module
from .parser import Parser


_MAIN_MODULE_NAME = '@main'
_BUILTIN_MODULE_NAME = '@builtin'


class Program:

    def __init__(self, data_sources):
        self.data_sources = data_sources
        self.modules = {}

    def parse(self):
        for data_source in self.data_sources:
            Parser(self, data_source).parse()

    def get_module(self, name):
        return self.modules.setdefault(name, Module(name))

    def get_main_module(self):
        return self.get_module(_MAIN_MODULE_NAME)

    def get_builtin_module(self):
        return self.get_module(_BUILTIN_MODULE_NAME)

    def get_default_module(self):
        return self.get_main_module()
