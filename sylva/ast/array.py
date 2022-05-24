import typing

from functools import cached_property

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors, utils
from ..location import Location
from .defs import TypeDef
from .expr import LiteralExpr, ValueExpr
from .number import IntType
from .pointer import ReferencePointerExpr, ReferencePointerType
from .range import RangeType
from .reflection_lookup import ReflectionLookupMixIn
from .str import StrType
from .sylva_type import SylvaParamType, SylvaType
from .type_singleton import TypeSingletons


@define(eq=False, slots=True)
class MonoArrayType(SylvaType, ReflectionLookupMixIn):
    element_type: SylvaType
    element_count: int = field()
    implementations: typing.List = []
    llvm_type: ir.Type | None = field(init=False)

    @cached_property
    def mname(self):
        return ''.join([
            '1a',
            self.element_type.mangle(),
            utils.len_prefix(str(self.element_count))
        ])

    # pylint: disable=unused-argument
    @element_count.validator
    def check_element_count(self, attribute, value):
        if value is not None and value <= 0:
            raise errors.EmptyArray(self.location)

    @llvm_type.default
    def _llvm_type_factory(self):
        return ir.ArrayType(self.element_type.llvm_type, self.element_count)

    # pylint: disable=no-self-use
    def get_reflection_attribute_type(self, location, name):
        if name == 'name':
            return StrType
        if name == 'size':
            return IntType
        if name == 'count':
            return IntType
        if name == 'element_type':
            return SylvaType
        if name == 'indices':
            return RangeType

    def reflect_attribute(self, location, name):
        # [FIXME] These need to be Sylva expressions that evaluate to LLVM
        #         values
        if name == 'name':
            return 'array'
        if name == 'size':
            return self.element_count * self.element_type.size # [TODO]
        if name == 'count':
            return self.element_count
        if name == 'element_type':
            return self.element_type
        if name == 'indices':
            return range(0, self.element_count + 1)


# Here, we want some way of saying "this type sort of exists without an
# element_count, but in most contexts it has to have one"
@define(eq=False, slots=True)
class ArrayType(SylvaParamType):
    monomorphizations: typing.List[MonoArrayType]
    implementation_builders: typing.List = []


@define(eq=False, slots=True)
class ArrayLiteralExpr(LiteralExpr):
    type: MonoArrayType

    @classmethod
    def FromRawValue(cls, location, element_type, raw_value):
        return cls(location, element_type, len(raw_value), raw_value)


@define(eq=False, slots=True)
class ArrayExpr(ValueExpr, ReflectionLookupMixIn):
    type: MonoArrayType

    def get_reflection_attribute_type(self, location, name):
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

    def reflect_attribute(self, location, name):
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
