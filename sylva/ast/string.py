import typing

from attrs import define, field

from .attribute_lookup import AttributeLookupMixIn
from .dynarray import DynarrayExpr, MonoDynarrayType
from .function import FunctionType
from .number import IntType
from .str import StrType
from .type_mapping import Attribute
from .type_singleton import TypeSingletons
from ..location import Location


@define(eq=False, slots=True)
class StringType(MonoDynarrayType, AttributeLookupMixIn):
    llvm_type = field(init=False)

    def mangle(self):
        return '6string'

    @llvm_type.default
    def _llvm_type_factory(self):
        u8 = IntType(Location.Generate(), 8, signed=False)
        return MonoDynarrayType(element_type=u8).llvm_type

    def get_attribute(self, location, name):
        if name == 'get_length':
            return Attribute(
                location=Location.Generate(),
                name='get_length',
                type=FunctionType.Def(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=TypeSingletons.UINT.value
                )
            )

    def get_reflection_attribute_type(self, location, name):
        # pylint: disable=consider-using-in
        if name == 'name':
            return StrType(
                location=Location.Generate(),
                value=bytearray('string', encoding='utf-8'),
            )
        if name == 'size':
            return TypeSingletons.UINT.value

    def reflect_attribute(self, location, name):
        if name == 'name':
            return 'string'
        if name == 'size':
            return self.get_size()

    def get_value_expr(self, location):
        return StringExpr(location=location, type=self)


@define(eq=False, slots=True)
class StringExpr(DynarrayExpr, AttributeLookupMixIn):
    type: typing.Any
