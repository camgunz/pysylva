from functools import cached_property

from .. import errors, utils
from .fn import MonoFnType
from .sylva_type import SylvaType
from .value import Value


class IfaceType(SylvaType):

    def __init__(self, location, functions):
        SylvaType.__init__(self, location)

        dupes = utils.get_dupes(x.name for x in functions)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

        self.functions = functions

    def get_attribute(self, name):
        for func_attr in self.functions:
            if func_attr.name == name:
                return func_attr.type
        return super().get_attribute(name)

    def emit_attribute_lookup(self, module, builder, scope, name):
        f = self.get_attribute(name)
        if f is not None:
            return Value(
                location=f.location, name=name, value=f, type=MonoFnType
            )
        return super().emit_attribute_lookup(module, builder, scope, name)

    def add_implementation(self, implementation):
        self.implementations.append(implementation)

    @cached_property
    def mname(self):
        return ''.join(['if', ''.join(f.type.mname for f in self.functions)])
