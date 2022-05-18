import typing

from attrs import define
from llvmlite import ir # type: ignore

from .. import errors
from .expr import Expr, LLVMExprMixIn, ValueExpr
from .operator import AttributeLookupMixIn, ReflectionLookupMixIn
from .sylva_type import LLVMTypeMixIn, SylvaType


@define(eq=False, slots=True)
class BasePointerType(SylvaType,
                      LLVMTypeMixIn,
                      AttributeLookupMixIn,
                      ReflectionLookupMixIn):
    referenced_type: SylvaType
    is_exclusive: bool
    implementations: typing.List = []

    def get_llvm_type(self, module):
        return ir.PointerType(self.referenced_type.get_llvm_type(module))

    def get_attribute(self, location, name):
        if not isinstance(self.referenced_type, AttributeLookupMixIn):
            raise errors.ImpossibleLookup(location)
        return self.referenced_type.get_attribute(location, name)

    def get_reflection_attribute_type(self, location, name, module):
        return self.referenced_type.get_reflection_attribute_type(
            location, name, module
        )


@define(eq=False, slots=True)
class ReferencePointerType(BasePointerType):
    pass


@define(eq=False, slots=True)
class OwnedPointerType(BasePointerType):
    is_exclusive: bool = True


@define(eq=False, slots=True)
class BasePointerExpr(ValueExpr):
    type: BasePointerType

    @property
    def referenced_type(self):
        return self.type.referenced_type

    @property
    def is_exclusive(self):
        return self.type.is_exclusive


@define(eq=False, slots=True)
class ReferencePointerExpr(BasePointerExpr):
    type: ReferencePointerType
    value: Expr


@define(eq=False, slots=True)
class MovePointerExpr(BasePointerExpr):
    type: OwnedPointerType
    value: Expr


@define(eq=False, slots=True)
class OwnedPointerExpr(BasePointerExpr):
    type: OwnedPointerType


@define(eq=False, slots=True)
class GetElementPointerExpr(Expr, LLVMExprMixIn):
    obj: Expr # [FIXME] This... has to be some kind of LLVM value
    index: int
    name: str | None

    def emit_llvm_expr(self, module, builder):
        return builder.gep(
            self.obj, [self.index], inbounds=True, name=self.name
        )
