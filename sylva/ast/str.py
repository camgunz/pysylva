import typing

from functools import cached_property

from attrs import define

from ..location import Location
from ..utils import mangle
from .array import ArrayType, MonoArrayType
from .attribute_lookup import AttributeLookupMixIn
from .expr import LiteralExpr
from .function import FunctionExpr, FunctionType
from .number import IntType, IntLiteralExpr
from .statement import ReturnStmt
from .type_mapping import Attribute
from .type_singleton import TypeSingletons


@define(eq=False, slots=True)
class MonoStrType(MonoArrayType):
    value: bytearray
    element_type: IntType = TypeSingletons.I8.value
    implementations: typing.List = []

    @classmethod
    def FromValue(cls, location, value):
        return cls(location=location, element_count=len(value), value=value)

    def get_value_expr(self, location):
        return StrLiteralExpr(location=location, type=self, value=self.value)

    @cached_property
    def mname(self):
        return mangle(['str', self.element_count])


@define(eq=False, slots=True)
class StrType(ArrayType):
    monomorphizations: typing.List[typing.Any] = []
    implementation_builders: typing.List = []


@define(eq=False, slots=True)
class StrLiteralExpr(LiteralExpr, AttributeLookupMixIn):
    type: MonoStrType

    # pylint: disable=arguments-differ
    @classmethod
    def FromRawValue(cls, location, raw_value):
        # [NOTE] I suppose this is where we'd configure internal string
        #        encoding.
        encoded_data = bytearray(raw_value[1:-1], encoding='utf-8')
        return cls(
            location,
            type=MonoStrType.FromValue(location, encoded_data),
            value=encoded_data
        )

    def get_attribute(self, location, name):
        if name == 'get_length':
            return Attribute(
                name='get_length',
                type=FunctionType(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=TypeSingletons.UINT.value
                )
            )

    def emit_attribute_lookup(self, location, name):
        if name == 'get_length':
            return FunctionExpr(
                name='get_length',
                location=Location.Generate(),
                type=self.get_attribute(location, 'get_length')[1],
                code=[
                    ReturnStmt(
                        location=Location.Generate(),
                        expr=IntLiteralExpr(
                            location=location,
                            type=TypeSingletons.UINT.value,
                            value=len(self.value)
                        )
                    )
                ]
            )

    def get_reflection_attribute_type(self, location, name):
        # pylint: disable=consider-using-in
        if name == 'size' or name == 'count':
            return self.type.get_reflection_attribute_type(location, name)

    def reflect_attribute(self, location, name):
        if name == 'size':
            return len(self.value)
        if name == 'count':
            return len(self.value.decode('utf-8'))
