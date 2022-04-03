from collections import defaultdict

from antlr4 import InputStream

from .ast import ModuleDecl, RequirementDecl
from .listener import SylvaParserListener
from .location import Location
from .module import Module
from .parser_utils import parse_with_listener


class ModuleScanner(SylvaParserListener):

    def __init__(self, stream=None):
        self._stream = stream
        self.module_declarations = []

    def exitModuleDecl(self, ctx):
        self.module_declarations.append(
            ModuleDecl(
                Location.FromContext(ctx, self._stream),
                ctx.children[1].getText()
            )
        )


class RequirementScanner(SylvaParserListener):

    def __init__(self, stream=None):
        self._stream = stream
        self.requirement_declarations = []

    def exitRequirementDecl(self, ctx):
        self.requirement_declarations.append(
            RequirementDecl(
                Location.FromContext(ctx, self._stream),
                ctx.children[1].getText()
            )
        )


class ModuleLoader:

    @staticmethod
    def get_module_declarations_from_streams(streams):
        module_declarations = []
        for s in streams:
            ms = ModuleScanner(s)
            parse_with_listener(s, ms)
            module_declarations.extend(ms.module_declarations)
        return module_declarations

    @staticmethod
    def gather_requirements_from_streams(streams):
        requirement_declarations = []
        for s in streams:
            rs = RequirementScanner(s)
            parse_with_listener(s, rs)
            requirement_declarations.extend(rs.requirement_declarations)
        seen = set()
        return [
            req for req in requirement_declarations
            if not req.name in seen and not seen.add(req.name)
        ]

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
                data = str(s)[loc.index:next_loc.index]
            else:
                data = str(s)[loc.index:]

            stream = InputStream(data + '\n')
            stream.name = loc.stream_name
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
