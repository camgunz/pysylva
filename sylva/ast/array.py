from functools import cached_property

from llvmlite import ir

from .. import errors, utils
from ..location import Location
from .attribute import Attribute
from .literal import LiteralExpr
from .sylva_type import SylvaParamType, SylvaType


def array_implementation_builder(array_type):
    from .type_singleton import TypeSingletons

    # name         | str(5) | 'array'
    # size         | uint   | element_count * element_type.size
    # count        | uint   | element_count
    # element_type | type   | element_type
    # indices      | range  | range(0, element_count + 1)
    str_five = TypeSingletons.STR.get_or_create_monomorphization(
        Location.Generate(), 5
    )

    # pylint: disable=unused-argument
    def emit_name_param(obj, location, module, builder, scope):
        return ir.Constant(
            str_five.llvm_type, bytearray('array', encoding='utf-8')
        )

    # pylint: disable=unused-argument
    def emit_count_param(obj, location, module, builder, scope):
        return ir.Constant(TypeSingletons.UINT.llvm_type, obj.element_count)

    array_type.set_attribute(
        Attribute(
            location=Location.Generate(),
            name='name',
            type=str_five,
            func=emit_name_param
        )
    )

    array_type.set_attribute(
        Attribute( # yapf: disable
            location=Location.Generate(),
            name='count',
            type=TypeSingletons.UINT,
            func=emit_count_param
        )
    )


class MonoArrayType(SylvaType):

    def __init__(self, location, element_type, element_count):
        if element_count <= 0:
            raise errors.EmptyArray(self.location)
        SylvaType.__init__(self, location)
        self.element_type = element_type
        self.element_count = element_count
        self.llvm_type = ir.ArrayType(element_type.llvm_type, element_count)

    @cached_property
    def mname(self):
        return ''.join([
            '1a',
            self.element_type.mname,
            utils.len_prefix(str(self.element_count))
        ])

    def __eq__(self, other):
        return (
            SylvaType.__eq__(self, other) and
            other.element_type == self.element_type and
            other.element_count == self.element_count
        )


class ArrayType(SylvaParamType):

    def __init__(self, location, implementation_builders=None):
        SylvaParamType.__init__(
            self,
            location,
            implementation_builders=implementation_builders or
            [array_implementation_builder]
        )

    def get_or_create_monomorphization(
        self, location, element_type, element_count
    ):
        for mm in self.monomorphizations:
            if mm.element_type != element_type:
                continue
            if mm.element_count != element_count:
                continue
            return mm

        mm = MonoArrayType(
            location, element_type=element_type, element_count=element_count
        )

        self.add_monomorphization(mm)

        return mm

    # def get_reflection_attribute(self, location, name):
    #     if name == 'type':
    #         return self.type
    #     if name == 'bytes':
    #         return ReferencePointerType(
    #             referenced_type=MonoArrayType(
    #                 Location.Generate(),
    #                 element_type=TypeSingletons.U8,
    #                 element_count=self.type.get_size()
    #             )
    #         )

    # def emit_reflection_lookup(self, location, module, builder, scope, name):
    #     if name == 'type':
    #         # [FIXME]
    #         return SylvaType
    #     if name == 'bytes':
    #         # [NOTE] Just overriding the type here _probably_ works, but only
    #         #        implicitly. It would be better if we had explicit
    #         #        support throughout.
    #         return ReferencePointerExpr(
    #             location=Location.Generate(),
    #             type=ReferencePointerType(
    #                 referenced_type=MonoArrayType(
    #                     Location.Generate(),
    #                     element_type=TypeSingletons.U8,
    #                     element_count=self.type.get_size()
    #                 )
    #             ),
    #             expr=self
    #         )


class ArrayLiteralExpr(LiteralExpr):

    def __init__(self, location, value):
        # [NOTE] We might know the type already because of the syntax:
        #       [int * 3][1i, 2i, 3i]
        from .type_singleton import TypeSingletons

        if len(value) == 0:
            raise errors.EmptyArray(location)

        first_type = value[0].type
        for v in value[1:]:
            if v.type != first_type:
                raise errors.MismatchedElementType(first_type, v)

        LiteralExpr.__init__(
            self,
            location,
            TypeSingletons.ARRAY.get_or_create_monomorphization(
                location, first_type, len(value)
            ),
            value
        )
