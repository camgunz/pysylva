import typing

from functools import cached_property

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors, utils
from .expr import Expr, ValueExpr
from .attribute_lookup import AttributeLookupMixIn
from .reflection_lookup import ReflectionLookupMixIn
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class BasePointerType(SylvaType, AttributeLookupMixIn, ReflectionLookupMixIn):
    referenced_type: SylvaType
    is_exclusive: bool
    implementations: typing.List = []
    llvm_type: ir.Type | None = field(init=False)

    @llvm_type.default
    def _llvm_type_factory(self):
        return ir.PointerType(self.referenced_type.llvm_type)

    def get_attribute(self, location, name):
        if not isinstance(self.referenced_type, AttributeLookupMixIn):
            raise errors.ImpossibleLookup(location)
        return self.referenced_type.get_attribute(location, name)

    def get_reflection_attribute_type(self, location, name):
        return self.referenced_type.get_reflection_attribute_type(
            location, name
        )


@define(eq=False, slots=True)
class ReferencePointerType(BasePointerType):

    @cached_property
    def mname(self):
        return ''.join(['2rp', self.referenced_type.mname])


@define(eq=False, slots=True)
class ExclusiveReferencePointerType(BasePointerType):
    is_exclusive: bool = True

    @cached_property
    def mname(self):
        return ''.join(['2xp', self.referenced_type.mname])


@define(eq=False, slots=True)
class OwnedPointerType(BasePointerType):
    is_exclusive: bool = True

    @cached_property
    def mname(self):
        return ''.join(['2op', self.referenced_type.mname])


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
class OwnedPointerExpr(BasePointerExpr):
    type: OwnedPointerType


@define(eq=False, slots=True)
class MovePointerExpr(BasePointerExpr):
    type: OwnedPointerType
    value: Expr


@define(eq=False, slots=True)
class GetElementPointerExpr(Expr):
    obj: Expr
    index: int
    name: str | None

    # pylint: disable=unused-argument
    def emit(self, module, builder, scope):
        return builder.gep(
            self.obj, [self.index], inbounds=True, name=self.name
        )
