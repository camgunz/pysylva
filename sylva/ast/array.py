from functools import cached_property

from attrs import define, field
from llvmlite import ir

from .. import errors, utils
from ..location import Location
from .defs import TypeDef
from .expr import LiteralExpr, ValueExpr
from .pointer import ReferencePointerExpr, ReferencePointerType
from .reflection_lookup import ReflectionAttribute, ReflectionLookupMixIn
from .sylva_type import SylvaParamType, SylvaType
from .type_singleton import TypeSingletons


def array_implementation_builder(array_type):
    # name         | str(5) | 'array'
    # size         | uint   | element_count * element_type.size
    # count        | uint   | element_count
    # element_type | type   | element_type
    # indices      | range  | range(0, element_count + 1)
    str_five = TypeSingletons.STR.value.get_or_create_monomorphization(5)

    array_type.set_reflection_attribute(
        ReflectionAttribute(
            name='name', type=str_five, func=lambda obj, location: 'array'
        )
    )

    array_type.set_reflection_attribute(
        ReflectionAttribute( # yapf: disable
            name='count',
            type=TypeSingletons.UINT.value,
            func=lambda obj, location: obj.element_count
        )
    )


@define(eq=False, slots=True)
class MonoArrayType(SylvaType):
    element_type = field()
    element_count = field()

    @cached_property
    def mname(self):
        return ''.join([
            '1a',
            self.element_type.mangle(),
            utils.len_prefix(str(self.element_count))
        ])

    @element_count.validator
    def check_element_count(self, attribute, value):
        if value is not None and value <= 0:
            raise errors.EmptyArray(self.location)

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return ir.ArrayType(self.element_type.llvm_type, self.element_count)


@define(eq=False, slots=True)
class ArrayType(SylvaParamType):
    implementation_builders = field(
        init=False, default=[array_implementation_builder]
    )

    def get_or_create_monomorphization(self, element_type, element_count):
        for mm in self.monomorphizations:
            if mm.element_type != element_type:
                continue
            if mm.element_count != element_count:
                continue
            return mm

        mm = MonoArrayType(
            element_type=element_type, element_count=element_count
        )
        self.add_monomorphization(mm)

        return mm


@define(eq=False, slots=True)
class ArrayLiteralExpr(LiteralExpr):

    @classmethod
    def FromRawValue(cls, location, element_type, raw_value):
        return cls(location, element_type, len(raw_value), raw_value)


@define(eq=False, slots=True)
class ArrayExpr(ValueExpr, ReflectionLookupMixIn):

    def get_reflection_attribute(self, location, name):
        if name == 'type':
            return self.type
        if name == 'bytes':
            return ReferencePointerType(
                referenced_type=MonoArrayType(
                    Location.Generate(),
                    element_type=TypeSingletons.U8,
                    element_count=self.type.get_size()
                )
            )

    def emit_reflection_lookup(self, location, module, builder, scope, name):
        if name == 'type':
            # [FIXME]
            return SylvaType
        if name == 'bytes':
            # [NOTE] Just overriding the type here _probably_ works, but only
            #        implicitly. It would be better if we had explicit support
            #        throughout.
            return ReferencePointerExpr(
                location=Location.Generate(),
                type=ReferencePointerType(
                    referenced_type=MonoArrayType(
                        Location.Generate(),
                        element_type=TypeSingletons.U8,
                        element_count=self.type.get_size()
                    )
                ),
                expr=self
            )


@define(eq=False, slots=True)
class ArrayDef(TypeDef):

    @cached_property
    def mname(self):
        return ''.join([utils.len_prefix(self.name), self.type.mname])
