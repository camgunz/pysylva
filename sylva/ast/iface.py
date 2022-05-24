from functools import cached_property

from attrs import define, field

from .. import errors, utils
from .attribute_lookup import AttributeLookupMixIn
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

    def add_implementation(self, implementation):
        self.implementations.append(implementation)

    @cached_property
    def mname(self):
        return ''.join(['if', ''.join(f.type.mname for f in self.functions)])
