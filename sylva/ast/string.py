import typing

from functools import cached_property

from attrs import define, field

from ..location import Location
from .attribute_lookup import AttributeLookupMixIn
from .dynarray import DynarrayExpr, MonoDynarrayType
from .function import FunctionType, MonoFunctionType
from .str import StrType
from .type_mapping import Attribute
from .type_singleton import TypeSingletons


@define(eq=False, slots=True)
class StringType(MonoDynarrayType, AttributeLookupMixIn):
    llvm_type = field(init=False)

    @llvm_type.default
    def _llvm_type_factory(self):
        return MonoDynarrayType(element_type=TypeSingletons.U8.value).llvm_type

    def get_attribute(self, location, name):
        if name == 'get_length':
            return Attribute(
                location=Location.Generate(),
                name='get_length',
                type=FunctionType(
                    location=Location.Generate(),
                    monomorphizations=[
                        MonoFunctionType(
                            location=Location.Generate(),
                            parameters=[],
                            return_type=TypeSingletons.UINT.value
                        )
                    ]
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

    @cached_property
    def mname(self):
        return '6string'


@define(eq=False, slots=True)
class StringExpr(DynarrayExpr, AttributeLookupMixIn):
    type: typing.Any
