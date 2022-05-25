from functools import cached_property

from attrs import define, field

from .. import errors, utils
from .attribute_lookup import AttributeLookupMixIn
from .expr import ValueExpr
from .fn import MonoFnType
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class IfaceType(SylvaType, AttributeLookupMixIn):
    functions = field()

    @functions.validator
    def check_functions(self, attribute, functions):
        dupes = utils.get_dupes(x.name for x in functions)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

    def get_attribute(self, location, name):
        for func_attr in self.functions:
            if func_attr.name == name:
                return func_attr.type
        return super().get_attribute(location, name)

    def emit_attribute_lookup(self, location, module, builder, scope, name):
        f = self.get_attribute(location, name)
        if f is not None:
            return ValueExpr(location=location, type=MonoFnType, value=f)
        return super().emit_attribute_lookup(
            location, module, builder, scope, name
        )

    def add_implementation(self, implementation):
        self.implementations.append(implementation)

    @cached_property
    def mname(self):
        return ''.join(['if', ''.join(f.type.mname for f in self.functions)])
