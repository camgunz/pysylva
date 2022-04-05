from . import sylva

from .compiler import Compiler
from .module_loader import ModuleLoader
from .stdlib import Stdlib


class Program:

    def __init__(self, streams, stdlib_path=None, target_triple=None):
        # [TODO] Do some kind of searching
        self.stdlib_path = stdlib_path or 'stdlib'
        self.stdlib = Stdlib.FromPath(self.stdlib_path)
        self.stdlib_modules = {
            module.name: module
            for module in
            ModuleLoader.load_from_streams(self, self.stdlib.streams)
        }

        self.modules = {
            module.name: module
            for module in ModuleLoader.load_from_streams(self, streams)
        }

        for module in self.modules.values():
            module.resolve_requirements()

        ordered_modules = []
        for module in self.modules.values():
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

    def check(self):
        errors = []
        for module in self.modules.values():
            errors.extend(module.check())
        return errors

    def compile(self, output_folder):
        errors = []
        for module in self.modules.values():
            with open(output_folder / module.name, 'wb') as fobj:
                module_object_code, module_errors = module.compile()
                if module_errors:
                    errors.extend(module_errors)
                else:
                    fobj.write(module_object_code)
        return errors

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
