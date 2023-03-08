import lark

from sylva import sylva
from sylva.ast_builder import ASTBuilder
from sylva.module_loader import ModuleLoader
from sylva.scope_gatherer import ScopeGatherer
from sylva.parser import Parser


class Program:

    def __init__(self, streams, search_paths):
        self.modules = ModuleLoader(  # yapf: ignore
            frozenset(search_paths)
        ).load_streams(streams)

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
