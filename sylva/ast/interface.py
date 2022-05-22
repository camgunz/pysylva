import typing

from attrs import define, field

from .. import errors, utils
from .attribute_lookup import AttributeLookupMixIn
from .defs import Def
from .sylva_type import SylvaType
from .type_mapping import Attribute


@define(eq=False, slots=True)
class InterfaceType(SylvaType, AttributeLookupMixIn):
    functions: typing.List[Attribute] = field()
    implementations: typing.List = []

    # pylint: disable=unused-argument
    @functions.validator
    def check_functions(self, attribute, functions):
        dupes = utils.get_dupes(x.name for x in functions)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

    # pylint: disable=unused-argument
    def get_attribute(self, location, name):
        # pylint: disable=not-an-iterable
        for func_attr in self.functions:
            if func_attr.name == name:
                return func_attr.type

    def add_implementation(self, implementation):
        self.implementations.append(implementation)


@define(eq=False, slots=True)
class InterfaceDef(Def):
    type: InterfaceType
