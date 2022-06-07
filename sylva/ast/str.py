from functools import cached_property

from llvmlite import ir

from .. import utils
from ..location import Location
from .array import ArrayType, MonoArrayType
from .attribute import Attribute
from .attribute_lookup import AttributeLookupExpr
from .fn import Fn, MonoFnType
from .impl import Impl
from .literal import LiteralExpr
from .lookup import LookupExpr
from .parameter import Parameter
from .reflection_lookup import ReflectionLookupExpr
from .statement import ReturnStmt
from .sylva_type import SylvaType


def str_implementation_builder(str_type):
    from .type_singleton import IfaceSingletons, TypeSingletons

    # name  | str(3) | 'str'
    # size  | uint   | element_count * element_type.size
    # count | uint   | element_count
    str_three = None

    if str_type.element_count == 3:
        str_three = str_type
    else:
        str_three = TypeSingletons.STR.get_or_create_monomorphization(
            Location.Generate(), 3
        )

    # pylint: disable=unused-argument
    def emit_name_param(obj, location, module, builder, scope):
        return ir.Constant(
            str_three.llvm_type, bytearray('str', encoding='utf-8')
        )

    # pylint: disable=unused-argument
    def emit_count_param(obj, location, module, builder, scope):
        return ir.Constant(TypeSingletons.UINT.llvm_type, obj.element_count)

    str_type.set_attribute(
        Attribute(
            Location.Generate(),
            name='name',
            type=str_three,
            func=emit_name_param
        )
    )

    str_type.set_attribute(
        Attribute(
            location=Location.Generate(),
            name='count',
            type=TypeSingletons.UINT,
            func=emit_count_param
        )
    )

    get_length = Fn(
        location=Location.Generate(),
        name='get_length',
        type=MonoFnType(
            location=Location.Generate(),
            parameters=[
                Parameter(
                    location=Location.Generate(),
                    name='self',
                    type=TypeSingletons.POINTER.get_or_create_monomorphization(
                        Location.Generate(),
                        referenced_type=str_type,
                        is_reference=True,
                        is_exclusive=False,
                    )
                )
            ],
            return_type=TypeSingletons.UINT
        ),
        code=[
            ReturnStmt(
                location=Location.Generate(),
                expr=AttributeLookupExpr(
                    location=Location.Generate(),
                    type=TypeSingletons.UINT,
                    name='element_count',
                    obj=ReflectionLookupExpr(
                        location=Location.Generate(),
                        type=SylvaType,
                        name='type',
                        obj=LookupExpr(
                            location=Location.Generate(),
                            type=str_type,
                            name='self',
                        ),
                    ),
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


class MonoStrType(MonoArrayType):

    def __init__(self, location, element_count):
        from .type_singleton import TypeSingletons

        MonoArrayType.__init__(
            self, location, TypeSingletons.U8, element_count
        )

    @cached_property
    def mname(self):
        return utils.mangle(['str', self.element_count])


class StrType(ArrayType):

    def __init__(self, location):
        ArrayType.__init__(self, location)
        self.add_implementation_builder(str_implementation_builder)


class StrLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        from .type_singleton import TypeSingletons

        LiteralExpr.__init__(
            self,
            location,
            TypeSingletons.STR.get_or_create_monomorphization(
                location, len(value)
            ),
            value
        )
