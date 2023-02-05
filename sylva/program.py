import lark
import llvmlite # type: ignore

from sylva import errors, sylva, target
from sylva.ast_builder import ASTBuilder
from sylva.module_loader import ModuleLoader
from sylva.parser import Parser


class Program:

    def __init__(self, streams, search_paths, target_triple=None):
        target.make_target(target_triple=target_triple)

        self.modules = ModuleLoader( # yapf: ignore
            frozenset(search_paths)
        ).load_streams(streams)

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
