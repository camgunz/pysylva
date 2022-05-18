import typing

from attrs import define
from llvmlite import ir # type: ignore

from .array import ArrayType
from .expr import LiteralExpr, ValueExpr
from .function import FunctionType
from .number import IntegerType
from .operator import ReflectionLookupMixIn
from .pointer import (
    GetElementPointerExpr, ReferencePointerExpr, ReferencePointerType
)
from .str import StrType
from .type_singleton import TypeSingletons
from .sylva_type import LLVMTypeMixIn, ParamTypeMixIn, SylvaType
from .type_mapping import Attribute
from ..location import Location


@define(eq=False, slots=True)
class MonoDynarrayType(SylvaType, LLVMTypeMixIn, ReflectionLookupMixIn):
    element_type: SylvaType
    implementations: typing.List = []

    def mangle(self):
        base = f'da{self.element_type.mangle()}'
        return f'{len(base)}{base}'

    def get_llvm_type(self, module):
        # yapf: disable
        return ir.LiteralStructType([
            TypeSingletons.UINT.value.get_llvm_type(module),     # capacity
            TypeSingletons.UINT.value.get_llvm_type(module),     # length
            self.element_type.get_llvm_type(module).as_pointer() # data
        ])

    # pylint: disable=no-self-use
    def get_reflection_attribute_type(self, location, name, module):
        if name == 'name':
            return StrType
        if name == 'size':
            return IntegerType
        if name == 'element_type':
            return self.element_type.type

    def reflect_attribute(self, location, name, module):
        # [FIXME] These need to be Sylva expressions that evaluate to LLVM
        #         values
        if name == 'name':
            return 'dynarray'
        if name == 'size':
            return self.get_size(module)
        if name == 'element_type':
            return self.element_type.get_llvm_type(module)

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

    def lookup_attribute(self, location, name, module):
        raise NotImplementedError()


@define(eq=False, slots=True)
class DynarrayType(SylvaType, ParamTypeMixIn):
    monomorphizations: typing.List[MonoDynarrayType]
    implementations: typing.List = []

    @classmethod
    def Def(cls, location, element_type):
        return cls(
            location=location,
            monomorphizations=[
                MonoDynarrayType(
                    location=location,
                    element_type=element_type,
                )
            ]
        )

    def add_monomorphization(self, location, element_type):
        index = len(self.monomorphizations)
        mdt = MonoDynarrayType(
            location=location,
            element_type=element_type,
        )
        self.monomorphizations.append(mdt)
        return index


@define(eq=False, slots=True)
class DynarrayLiteralExpr(LiteralExpr):
    type: DynarrayType

    @classmethod
    def FromRawValue(cls, location, element_type, raw_value):
        # [FIXME] This involves heap allocation, and is therefore a little
        #         tricker than this
        return cls(location, element_type, len(raw_value), raw_value)


@define(eq=False, slots=True)
class DynarrayExpr(ValueExpr, ReflectionLookupMixIn):
    type: DynarrayType

    # pylint: disable=no-self-use,unused-argument
    def get_attribute(self, location, name):
        if name == 'get_length':
            return Attribute(
                location=Location.Generate(),
                name='get_length',
                type=FunctionType.Def(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=TypeSingletons.UINT.value
                )
            )

    def lookup_attribute(self, location, name, module):
        raise NotImplementedError()

    def get_reflection_attribute_type(self, location, name, module):
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return ReferencePointerType(
                referenced_type=ArrayType(
                    Location.Generate(),
                    element_type=IntegerType(
                        Location.Generate(), 8, signed=False
                    ),
                    element_count=self.type.get_size(module)
                )
            )

    def reflect_attribute(self, location, name, module):
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
                        element_type=IntegerType(
                            Location.Generate(), 8, signed=False
                        ),
                        element_count=self.type.get_size(module)
                    )
                ),
                expr=self
            )
