from dataclasses import dataclass, field
from functools import cached_property

from sylva import errors, utils
from sylva.ast.expr import LiteralExpr
from sylva.ast.sylva_type import MonoType, ParamType, SylvaType


@dataclass(kw_only=True)
class MonoArrayType(MonoType):
    element_type: SylvaType
    element_count: int

    def __post_init__(self):
        if self.element_count <= 0:
            raise errors.EmptyArray(self.location)

    @cached_property
    def mname(self):
        return ''.join([
            '1a',
            self.element_type.mname,
            utils.len_prefix(str(self.element_count))
        ])


@dataclass(kw_only=True)
class ArrayType(ParamType):
    name: str = field(init=False, default='array')
    element_type: SylvaType

    # pylint: disable=arguments-differ
    def get_or_create_monomorphization(self, location, element_count):
        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(self.element_type, element_count):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoArrayType(
            location=location,
            element_type=self.element_type,
            element_count=element_count
        )
        self.monomorphizations.append(mm)

        return index, mm

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
    #         return MonoType
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

        if any(e.type != value[0].type for e in value[1:]):
            raise errors.InconsistentElementType(location, value[0].type)

        LiteralExpr.__init__(
            self,
            location=location,
            type=TypeSingletons.ARRAY.get_or_create_monomorphization(
                location, value[0].type, len(value)
            )[1],
            value=value
        )
