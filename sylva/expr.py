from dataclasses import dataclass, field
from typing import Any, Optional

from sylva import errors, utils
from sylva.location import Location
from sylva.builtins import (
    CPtrType,
    CVoidType,
    ComplexType,
    FloatType,
    IntType,
    StrType,
    SylvaObject,
    SylvaType,
)
from sylva.operator import Operator


@dataclass(kw_only=True)
class Expr(SylvaObject):
    location: Location = field(default_factory=Location.Generate)
    type: Optional[SylvaType]

    def eval(self, module):
        raise NotImplementedError()


@dataclass(kw_only=True)
class LookupExpr(Expr):
    name: str

    def eval(self, module):
        val = module.lookup(self.name)
        if val is None:
            raise errors.UndefinedSymbol(self.location, self.name)
        return val


@dataclass(kw_only=True)
class LiteralExpr(Expr):
    value: Any

    def eval(self, module):
        return self.value


@dataclass(kw_only=True)
class UnaryExpr(Expr):
    operator: Operator
    expr: Expr


@dataclass(kw_only=True)
class BinaryExpr(Expr):
    operator: Operator
    lhs: Expr
    rhs: Expr


@dataclass(kw_only=True)
class AttributeLookupExpr(Expr):
    name: str
    obj: Expr
    reflection: bool = False


@dataclass(kw_only=True)
class ReflectionLookupExpr(Expr):
    name: str
    obj: Expr


@dataclass(kw_only=True)
class CallExpr(Expr):
    function: Expr
    arguments: list[Expr]
    monomorphization_index: int = 0


@dataclass(kw_only=True)
class IntExpr(Expr):
    type: IntType


@dataclass(kw_only=True)
class FloatExpr(Expr):
    type: FloatType


@dataclass(kw_only=True)
class ComplexExpr(Expr):
    type: ComplexType


@dataclass(kw_only=True)
class CVoidExpr(Expr):
    type: CVoidType
    expr: Expr


@dataclass(kw_only=True)
class CPtrExpr(Expr):
    type: CPtrType
    expr: Expr


@dataclass(kw_only=True)
class IntLiteralExpr(LiteralExpr):
    type: IntType
    value: int

    def __post_init__(self):
        if utils.bits_required_for_int(self.value) > self.type.bits:
            raise errors.IntSizeExceeded(self.value)


@dataclass(kw_only=True)
class StrLiteralExpr(LiteralExpr):
    type: StrType
    value: bytes

    def __post_init__(self):
        self.value = self.value.encode('utf-8')
