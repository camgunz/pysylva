from functools import cached_property

from attrs import define, field
from llvmlite import ir

from ..location import Location
from ..utils import mangle
from .array import ArrayType, MonoArrayType
from .attribute_lookup import AttributeLookupExpr, AttributeLookupMixIn
from .expr import LiteralExpr
from .function import FunctionDef, FunctionType, MonoFunctionType
from .impl import Impl
from .lookup import LookupExpr
from .reflection_lookup import ReflectionLookupExpr
from .statement import ReturnStmt
from .sylva_type import SylvaType
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

    def emit_name_param(obj, location, module, builder, scope):
        return ir.Constant(
            str_three.llvm_type, bytearray('str', encoding='utf-8')
        )

    def emit_count_param(obj, location, module, builder, scope):
        return ir.Constant(
            TypeSingletons.UINT.value.llvm_type, obj.element_count
        )

    str_type.set_attribute(
        Attribute(name='name', type=str_three, func=emit_name_param)
    )

    str_type.set_attribute(
        Attribute(
            name='count',
            type=TypeSingletons.UINT.value,
            func=emit_count_param
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
                                referenced_type=str_type,
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
                    expr=ReflectionLookupExpr(
                        location=Location.Generate(),
                        type=SylvaType,
                        attribute='type',
                        expr=LookupExpr(
                            location=Location.Generate(), name='self'
                        ),
                        name='type'
                    )
                )
            )
        ]
    )

    impl = Impl(
        location=Location.Generate(),
        interface=IfaceSingletons.STRING.value,
        implementing_type=str_type,
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
