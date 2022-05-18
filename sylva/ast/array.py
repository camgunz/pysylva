import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .expr import LiteralExpr, ValueExpr
from .number import IntegerType
from .operator import ReflectionLookupMixIn
from .pointer import ReferencePointerExpr, ReferencePointerType
from .range import RangeType
from .str import StrType
from .sylva_type import LLVMTypeMixIn, ParamTypeMixIn, SylvaType
from .. import errors
from ..location import Location


@define(eq=False, slots=True)
class MonoArrayType(SylvaType, LLVMTypeMixIn, ReflectionLookupMixIn):
    element_type: SylvaType
    element_count: int = field()
    implementations: typing.List = []

    def mangle(self):
        base = f'a{self.element_type.mangle()}{self.element_count}'
        return f'{len(base)}{base}'

    # pylint: disable=unused-argument
    @element_count.validator
    def check_element_count(self, attribute, value):
        if value is not None and value <= 0:
            raise errors.EmptyArray(self.location)

    def get_llvm_type(self, module):
        return ir.ArrayType(
            self.element_type.get_llvm_type(module), self.element_count
        )

    # pylint: disable=no-self-use
    def get_reflection_attribute_type(self, location, name, module):
        if name == 'name':
            return StrType
        if name == 'size':
            return IntegerType
        if name == 'count':
            return IntegerType
        if name == 'element_type':
            return SylvaType
        if name == 'indices':
            return RangeType

    def reflect_attribute(self, location, name, module):
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
class ArrayType(SylvaType, ParamTypeMixIn):
    monomorphizations: typing.List[MonoArrayType] = []

    @classmethod
    def Def(cls, location, element_type, element_count):
        return cls(
            location=location,
            monomorphizations=[
                MonoArrayType(
                    location=location,
                    element_type=element_type,
                    element_count=element_count
                )
            ]
        )

    def add_monomorphization(self, location, element_type, element_count):
        index = len(self.monomorphizations)
        mat = MonoArrayType(
            location=location,
            element_type=element_type,
            element_count=element_count
        )
        self.monomorphizations.append(mat)
        return index


@define(eq=False, slots=True)
class ArrayLiteralExpr(LiteralExpr):
    type: ArrayType

    @classmethod
    def FromRawValue(cls, location, element_type, raw_value):
        return cls(location, element_type, len(raw_value), raw_value)


@define(eq=False, slots=True)
class ArrayExpr(ValueExpr, ReflectionLookupMixIn):
    type: ArrayType

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
            return SylvaType
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
