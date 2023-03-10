import lark

from sylva import errors, sylva
from sylva.ast_builder import ASTBuilder
from sylva.cffi import CModuleBuilder
from sylva.module_loader import ModuleLoader
from sylva.package import BinPackage, CLibPackage, LibPackage
from sylva.parser import Parser
from sylva.scope_gatherer import ScopeGatherer
from sylva.stream import Stream
from sylva.utils import read_toml_file


class Program:

    def __init__(self, package_file, deps_folder, c_preprocessor, libclang):
        package_def = read_toml_file(package_file)
        if package_def['type'] == 'bin':
            package = BinPackage(**package_def)
            streams = [Stream.FromPath(sf) for sf in package.source_files]
            self.modules = ModuleLoader(deps_folder).load_streams(streams)
        elif package_def['type'] == 'lib':
            package = LibPackage(**package_def)
            streams = [Stream.FromPath(sf) for sf in package.source_files]
            self.modules = ModuleLoader(deps_folder).load_streams(streams)
        elif package_def['type'] == 'clib':
            self.modules = [
                CModuleBuilder.build_module(
                    c_lib_package=CLibPackage(**package_def),
                    c_preprocessor=c_preprocessor,
                    libclang=libclang
                )
            ]
        else:
            raise errors.InvalidPackageType(package_file, package_def['type'])

        self.modules = ModuleLoader(deps_folder).load_streams(streams)

    def parse(self):
        parser = Parser()
        scope_gatherer = ScopeGatherer()

        module_trees = [ # yapf: ignore
            (module, location, parser.parse(location.stream.data))
            for module in self.modules.values()
            for location in module.locations
        ]

        for module, location, tree in module_trees:
            scope_gatherer.visit_topdown(tree)

        module_trees = [ # yapf: ignore
            ASTBuilder( # yapf: ignore
                program=self,
                module=module,
                location=location
            ).transform(tree)
            for module, location, tree in module_trees
        ]

        return lark.Tree(data='Program', children=module_trees)

    def compile(self, output_folder):
        raise NotImplementedError

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
