from attrs import define

from .dynarray import DynarrayExpr, MonoDynarrayType
from .function import FunctionType
from .number import IntegerType
from .operator import AttributeLookupMixIn
from .str import StrType
from .type_mapping import Attribute
from .type_singleton import TypeSingleton
from ..location import Location


@define(eq=False, slots=True)
class StringType(MonoDynarrayType, AttributeLookupMixIn):

    def mangle(self):
        return '6string'

    def get_llvm_type(self, module):
        u8 = IntegerType(Location.Generate(), 8, signed=False)
        return MonoDynarrayType(element_type=u8).get_llvm_type(module)

    def get_attribute(self, location, name):
        if name == 'get_length':
            return Attribute(
                location=Location.Generate(),
                name='get_length',
                type=FunctionType.Def(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=TypeSingleton.UINT.value
                )
            )

    def get_reflection_attribute_type(self, location, name, module):
        # pylint: disable=consider-using-in
        if name == 'name':
            return StrType(
                location=Location.Generate(),
                value=bytearray('string', encoding='utf-8'),
            )
        if name == 'size':
            return TypeSingleton.UINT.value

    def reflect_attribute(self, location, name, module):
        if name == 'name':
            return 'string'
        if name == 'size':
            return self.get_size(module)

    def get_value_expr(self, location):
        return StringExpr(location=location, type=self)


@define(eq=False, slots=True)
class StringExpr(DynarrayExpr, AttributeLookupMixIn):
    type: StringType
