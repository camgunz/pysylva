from collections import defaultdict

from antlr4 import InputStream

from .ast import ModuleStmt, RequirementStmt
from .listener import SylvaListener
from .location import Location
from .module import Module
from .parser_utils import parse_with_listener


class ModuleScanner(SylvaListener):

    def __init__(self, stream=None):
        self._stream = stream
        self.module_statements = []

    def exitModuleDecl(self, ctx):
        self.module_statements.append(
            ModuleStmt(
                Location.FromContext(ctx, self._stream),
                ctx.children[1].getText()
            )
        )


class RequirementScanner(SylvaListener):

    def __init__(self, stream=None):
        self._stream = stream
        self.requirement_statements = []

    def exitRequirementDecl(self, ctx):
        self.requirement_statements.append(
            RequirementStmt(
                Location.FromContext(ctx, self._stream),
                ctx.children[1].getText()
            )
        )


class ModuleLoader:

    @staticmethod
    def get_module_statements_from_streams(streams):
        module_statements = []
        for s in streams:
            ms = ModuleScanner(s)
            parse_with_listener(s, ms)
            module_statements.extend(ms.module_statements)
        return module_statements

    @staticmethod
    def gather_requirements_from_streams(streams):
        requirement_statements = []
        for s in streams:
            rs = RequirementScanner(s)
            parse_with_listener(s, rs)
            requirement_statements.extend(rs.requirement_statements)
        seen = set()
        return [
            req for req in requirement_statements
            if not req.name in seen and not seen.add(req.name)
        ]

    @staticmethod
    def load_from_streams(program, input_streams):
        names_to_streams = defaultdict(list)

        module_statements = (
            ModuleLoader.get_module_statements_from_streams(input_streams)
        )

        if not module_statements:
            return []

        for n, ms in enumerate(module_statements):
            loc = ms.location
            s = loc.stream
            next_loc = (
                module_statements[n + 1].location
                if n + 1 < len(module_statements) else None
            )

            if next_loc and s == next_loc.stream:
                data = str(s)[loc.index:next_loc.index]
            else:
                data = str(s)[loc.index:]

            stream = InputStream(data + '\n')
            stream.name = loc.stream_name
            names_to_streams[ms.name].append(stream)

        return [
            Module(
                program,
                name,
                streams,
                ModuleLoader.gather_requirements_from_streams(streams)
            ) for name,
            streams in names_to_streams.items()
        ]
