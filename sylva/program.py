from . import sylva

from .module_loader import ModuleLoader
from .stdlib import Stdlib
from .target import Target


class Program:

    def __init__(self, streams, stdlib_path=None, target_triple=None):
        self.target = Target(target_triple=target_triple)

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
        errors = []
        for module in self.modules.values():
            errors.extend(module.parse())
        return errors

    def compile(self, output_folder):
        errors = []
        for module in self.modules.values():
            module_object_code, module_errors = module.get_object_code()
            if module_errors:
                errors.extend(module_errors)
            else:
                with open(output_folder / module.name, 'wb') as fobj:
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
