from functools import cached_property

from attrs import define, field

from ..location import Location
from ..utils import mangle
from .array import ArrayType, MonoArrayType
from .attribute_lookup import AttributeLookupMixIn
from .expr import LiteralExpr
from .function import FunctionDef, FunctionExpr, FunctionType, MonoFunctionType
from .number import IntLiteralExpr
from .reflection_lookup import ReflectionAttribute
from .statement import ReturnStmt
from .type_mapping import Attribute, Parameter
from .type_singleton import IfaceSingletons, TypeSingletons


def str_implementation_builder(str_type):
    # name  | str(3) | 'str'
    # size  | uint   | element_count * element_type.size
    # count | uint   | element_count
    str_three = None

    if str_type.element_count == 3:
        str_three = str_type
    else:
        str_three = TypeSingletons.STR.value.get_or_create_monomorphization(3)

    str_type.set_reflection_attribute(
        ReflectionAttribute(
            name='name', type=str_three, func=lambda obj, location: 'str'
        )
    )

    str_type.set_reflection_attribute(
        ReflectionAttribute(
            name='count',
            type=TypeSingletons.UINT.value,
            func=lambda obj,
            location: obj.element_count
        )
    )

    get_length = FunctionDef(
        name='get_length',
        type=FunctionType(
            location=Location.Generate(),
            monomorphizations=[
                MonoFunctionType(
                    location=Location.Generate(),
                    parameters=[
                        Parameter(
                            location=Location.Generate(),
                            name='self',
                            type=ReferencePointerType(
                                referenced_type=new_str_type,
                            )
                        )
                    ],
                    return_type=TypeSingletons.UINT.value
                )
            ]
        ),
        code=[
            ReturnStmt(
                expr=AttributeLookupExpr(
                    location=Location.Generate(),
                    type=TypeSingletons.UINT.value,
                    attribute='element_count',
                    expr=AttributeLookupExpr(
                        location=Location.Generate(), name='self'
                    ),
                    reflection=True
                )
            )
        ]
    )

    impl = Implementation(
        location=Location.Generate(),
        interface=IfaceSingletons.STRING.value,
        implementing_type=new_str_type,
        funcs=[get_length]
    )

    IfaceSingletons.STRING.value.add_implementation(impl)
    str_type.add_implementation(impl)


@define(eq=False, slots=True)
class MonoStrType(MonoArrayType):
    value = field(default=bytearray())
    element_type = field(init=False, default=TypeSingletons.I8.value)

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
    implementation_builders = field(
        init=False, default=[str_implementation_builder]
    )

    def get_or_create_monomorphization(self, element_count):
        for mm in self.monomorphizations:
            if mm.element_count == element_count:
                return mm

        mm = MonoStrType(element_count=element_count)
        self.add_monomorphization(mm)

        return mm


@define(eq=False, slots=True)
class StrLiteralExpr(LiteralExpr, AttributeLookupMixIn):

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
