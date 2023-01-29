from dataclasses import dataclass, field

import lark

from sylva import errors
from sylva.location import Location
from sylva.parser import Parser
from sylva.stream import Stream


@dataclass(kw_only=True, frozen=True, slots=True)
class Requirement:
    name: str
    location: Location


@dataclass(kw_only=True, slots=True)
class Module:
    name: str
    locations: list[Location] = field(default_factory=list)
    requirements: list[Requirement] = field(default_factory=list)


class ModuleGatherer(lark.Visitor):

    """
    A Sylva program compiles source files. Internal requirements are
    checked after all modules have been gathered. External dependencies
    rely on module description files, which are single files in a
    program's search path.
    """

    def __init__(self, stream, modules):
        self._stream = stream
        self._modules = modules
        self._current_module = None

    def module_decl(self, tree):
        loc = Location.FromTree(tree, stream=self._stream)
        mod_name = tree.children[0].value

        if mod_name not in self._modules:
            mod = Module(name=mod_name, locations=[loc])
            self._modules[mod_name] = mod
        else:
            mod = self._modules[mod_name]
            mod.locations.append(loc)

        pmod = self._current_module
        self._current_module = mod

        if not pmod:
            return

        ploc = mod.locations[-2] if mod == pmod else pmod.locations[-1]
        loc = mod.locations[-1]

        ploc.stream = Stream(
            name=ploc.stream_name,
            data=ploc.stream.data[ploc.index:loc.index] + '\n'
        )

    def requirement_decl(self, tree):
        req = Requirement(
            location=Location.FromTree(tree, stream=self._stream),
            name=tree.children[0].value
        )

        if req.name not in [r.name for r in self._current_module.requirements]:
            self._current_module.requirements.append(req)


class RequirementLoader(lark.Visitor):

    def __init__(self, program, location, modules, missing):
        self._program = program
        self._stream = location.stream
        self._modules = modules
        self._missing = missing

    def requirement_decl(self, tree):
        req = Requirement(
            location=Location.FromTree(tree, stream=self._stream),
            name=tree.children[0].value
        )

        if req.name in self._modules:
            return

        req_path = self._program.get_requirement_path(req.name)

        if not req_path:
            self._missing.append(req)
            return

        self._program.register_required_module(
            Module(name=req.name, locations=[Location.FromPath(req_path)])
        )


class ModuleLoader:

    @staticmethod
    def load_from_streams(program, input_streams):
        parser = Parser()
        modules = {}

        for stream in input_streams:
            gatherer = ModuleGatherer(stream, modules)
            try:
                gatherer.visit(parser.parse(stream.data))
            except lark.UnexpectedToken as e:
                raise errors.UnexpectedToken(
                    Location.FromUnexpectedTokenError(e, stream=stream),
                    e.token.value,
                    e.expected
                ) from None

        missing = []
        for module in modules.values():
            for loc in module.locations:
                req_loader = RequirementLoader(program, loc, modules, missing)
                req_loader.visit(parser.parse(loc.stream.data))

        if missing:
            raise errors.MissingRequirements(missing)

        return modules
