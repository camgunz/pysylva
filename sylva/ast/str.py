import typing

from attrs import define

from .array import MonoArrayType
from .expr import LiteralExpr
from .function import FunctionExpr, FunctionType
from .number import IntType, IntLiteralExpr
from .operator import AttributeLookupMixIn
from .statement import ReturnStmt
from .type_mapping import Attribute
from .type_singleton import TypeSingletons
from ..location import Location


@define(eq=False, slots=True)
class StrType(MonoArrayType):
    value: bytearray
    element_type: IntType = TypeSingletons.I8.value
    implementations: typing.List = []

    def mangle(self):
        base = f'str{self.element_type.mangle()}{self.element_count}'
        return f'{len(base)}{base}'

    @classmethod
    def FromValue(cls, location, value):
        return cls(location=location, element_count=len(value), value=value)

    def get_value_expr(self, location):
        return StrLiteralExpr(location=location, type=self, value=self.value)


@define(eq=False, slots=True)
class StrLiteralExpr(LiteralExpr, AttributeLookupMixIn):
    type: StrType

    # pylint: disable=arguments-differ
    @classmethod
    def FromRawValue(cls, location, raw_value):
        # [NOTE] I suppose this is where we'd configure internal string
        #        encoding.
        encoded_data = bytearray(raw_value[1:-1], encoding='utf-8')
        return cls(
            location,
            type=StrType.FromValue(location, encoded_data),
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

    def emit_attribute_lookup(self, location, name, module):
        if name == 'get_length':
            return FunctionExpr(
                name='get_length',
                location=Location.Generate(),
                type=self.get_attribute(location, 'get_length')[1],
                code=[
                    ReturnStmt(
                        location=Location.Generate(),
                        expr=IntLiteralExpr.Platform(
                            location=location,
                            signed=False,
                            value=len(self.value)
                        )
                    )
                ]
            )

    def get_reflection_attribute_type(self, location, name, module):
        # pylint: disable=consider-using-in
        if name == 'size' or name == 'count':
            return self.type.get_reflection_attribute_type(
                location, name, module
            )

    def reflect_attribute(self, location, name, module):
        if name == 'size':
            return len(self.value)
        if name == 'count':
            return len(self.value.decode('utf-8'))
