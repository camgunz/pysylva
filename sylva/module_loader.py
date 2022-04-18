from collections import defaultdict

import lark

from .ast import ModuleDecl, RequirementDecl
from .location import Location
from .module import Module
from .parser import Lark_StandAlone as Parser
from .stream import Stream


class ModuleDeclVisitor(lark.Visitor):

    def __init__(self, stream, decls):
        self._stream = stream
        self._decls = decls

    def module_decl(self, tree):
        loc = Location.FromTree(tree, stream=self._stream)
        self._decls.append(ModuleDecl(loc, tree.children[0].children[0].value))


class RequirementDeclVisitor(lark.Visitor):

    def __init__(self, stream, decls):
        self._stream = stream
        self._decls = decls
        self._seen = set()

    def requirement_decl(self, tree):
        rd_name = tree.children[0].children[0].value
        if rd_name in self._seen:
            return

        self._seen.add(rd_name)

        loc = Location.FromTree(tree, stream=self._stream)
        self._decls.append(RequirementDecl(loc, rd_name))


class ModuleLoader:

    @staticmethod
    def get_module_declarations_from_streams(streams):
        mod_decls = []
        for s in streams:
            ModuleDeclVisitor(s, mod_decls).visit(Parser().parse(s.data))
        return mod_decls

    @staticmethod
    def gather_requirements_from_streams(streams):
        req_decls = []
        for s in streams:
            RequirementDeclVisitor(s, req_decls).visit(Parser().parse(s.data))
        return req_decls

    @staticmethod
    def load_from_streams(program, input_streams):
        names_to_streams = defaultdict(list)

        module_declarations = (
            ModuleLoader.get_module_declarations_from_streams(input_streams)
        )

        if not module_declarations:
            return []

        for n, md in enumerate(module_declarations):
            loc = md.location
            s = loc.stream
            next_loc = (
                module_declarations[n + 1].location
                if n + 1 < len(module_declarations) else None
            )

            if next_loc and s == next_loc.stream:
                data = s.data[loc.index:next_loc.index]
            else:
                data = s.data[loc.index:]

            stream = Stream(name=loc.stream_name, data=data + '\n')
            names_to_streams[md.name].append(stream)

        return [
            Module(
                program,
                name,
                streams,
                ModuleLoader.gather_requirements_from_streams(streams)
            ) for name,
            streams in names_to_streams.items()
        ]
