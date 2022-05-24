import typing

from functools import cached_property

from attrs import define, field
from llvmlite import ir # type: ignore

from ..location import Location
from .array import ArrayType
from .expr import LiteralExpr, ValueExpr
from .function import FunctionType, MonoFunctionType
from .number import IntType
from .pointer import (
    GetElementPointerExpr, ReferencePointerExpr, ReferencePointerType
)
from .reflection_lookup import ReflectionLookupMixIn
from .str import StrType
from .type_singleton import TypeSingletons
from .sylva_type import SylvaParamType, SylvaType
from .type_mapping import Attribute


@define(eq=False, slots=True)
class MonoDynarrayType(SylvaType, ReflectionLookupMixIn):
    element_type: SylvaType
    implementations: typing.List = []
    llvm_type = field(init=False)

    @llvm_type.default
    def _llvm_type_factory(self):
        # yapf: disable
        return ir.LiteralStructType([
            TypeSingletons.UINT.value.llvm_type,     # capacity
            TypeSingletons.UINT.value.llvm_type,     # length
            self.element_type.llvm_type.as_pointer() # data
        ])

    # pylint: disable=no-self-use
    def get_reflection_attribute_type(self, location, name):
        if name == 'name':
            return StrType
        if name == 'size':
            return IntType
        if name == 'element_type':
            return self.element_type.type

    def reflect_attribute(self, location, name):
        # [FIXME] These need to be Sylva expressions that evaluate to LLVM
        #         values
        if name == 'name':
            return 'dynarray'
        if name == 'size':
            return self.get_size()
        if name == 'element_type':
            return self.element_type.llvm_type

    def get_attribute(self, location, name):
        if name == 'capacity':
            return GetElementPointerExpr(
                location=location,
                index=0,
                name='capacity'
            )
        if name == 'length':
            return GetElementPointerExpr(
                location=location,
                index=1,
                name='length'
            )
        if name == 'data':
            return GetElementPointerExpr(
                location=location,
                index=2,
                name='data'
            )
        for impl in self.implementations:
            for func in impl.funcs:
                if func.name == name:
                    return func

    def lookup_attribute(self, location, name):
        raise NotImplementedError()

    @cached_property
    def mname(self):
        return ''.join(['2da', self.element_type.mangle()])


@define(eq=False, slots=True)
class DynarrayType(SylvaParamType):
    monomorphizations: typing.List[MonoDynarrayType]
    implementations: typing.List = []


@define(eq=False, slots=True)
class DynarrayLiteralExpr(LiteralExpr):
    type: MonoDynarrayType

    @classmethod
    def FromRawValue(cls, location, element_type, raw_value):
        # [FIXME] This involves heap allocation, and is therefore a little
        #         tricker than this
        return cls(location, element_type, len(raw_value), raw_value)


@define(eq=False, slots=True)
class DynarrayExpr(ValueExpr, ReflectionLookupMixIn):
    type: typing.Any

    # pylint: disable=no-self-use,unused-argument
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

    def lookup_attribute(self, location, name):
        raise NotImplementedError()

    def get_reflection_attribute_type(self, location, name):
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return ReferencePointerType(
                referenced_type=ArrayType(
                    Location.Generate(),
                    element_type=TypeSingletons.U8,
                    element_count=self.type.get_size()
                )
            )

    def reflect_attribute(self, location, name):
        if name == 'type':
            # [FIXME]
            return self.type
        if name == 'bytes':
            # [NOTE] Just overriding the type here _probably_ works, but only
            #        implicitly. It would be better if we had explicit support
            #        throughout.
            return ReferencePointerExpr(
                location=Location.Generate(),
                type=ReferencePointerType(
                    referenced_type=ArrayType(
                        Location.Generate(),
                        element_type=TypeSingletons.U8,
                        element_count=self.type.get_size()
                    )
                ),
                expr=self
            )
