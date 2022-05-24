import llvmlite # type: ignore

from . import sylva, sylva_builtins

from .module_loader import ModuleLoader
from .stdlib import Stdlib
from .target import get_target, make_target


class Program:

    def __init__(self, streams, stdlib_path=None, target_triple=None):
        make_target(target_triple=target_triple)

        # [TODO] Do some kind of searching
        self.stdlib_path = stdlib_path or 'stdlib'
        self.stdlib = Stdlib.FromPath(self.stdlib_path)
        self.stdlib_modules = {
            'builtin': sylva_builtins.get_module(self),
            **{
                module.name: module
                for module in ModuleLoader.load_from_streams(
                    self, self.stdlib.streams
                )
            }
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
            parse_errors = module.parse()
            if parse_errors:
                errors.extend(parse_errors)
            else:
                llvm_module, compilation_errors = module.llvm_define()
                if compilation_errors:
                    errors.extend(compilation_errors)
                else:
                    llvm_mod_ref = (
                        llvmlite.binding.parse_assembly(str(llvm_module))
                    )
                    llvm_mod_ref.verify()
                    object_code = (
                        get_target().machine.emit_object(llvm_mod_ref)
                    )
                    with open(output_folder / module.name, 'wb') as fobj:
                        fobj.write(object_code)
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
