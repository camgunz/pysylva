from dataclasses import dataclass, field
from typing import Any, Optional, Union

from sylva import debug, errors, utils
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
    SylvaValue,
    parse_int_value,
)
from sylva.mod import Mod
from sylva.operator import Operator


@dataclass(kw_only=True)
class Expr(SylvaObject):
    location: Location = field(default_factory=Location.Generate)
    type: Optional[SylvaType] = None

    def eval(self, module):
        raise NotImplementedError()


@dataclass(kw_only=True)
class LookupExpr(Expr):
    name: str

    def eval(self, module: Mod) -> Union[Mod, SylvaType, SylvaValue]:
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
    obj: Any
    reflection: bool = False

    def eval(self, module: Mod):
        obj = self.obj.eval(module) if isinstance(self.obj, Expr) else self.obj
        return ( # yapf: ignore
            obj.reflection_lookup(self.name)
            if self.reflection
            else obj.lookup(self.name)
        )


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
        LiteralExpr.__post_init__(self)
        if utils.bits_required_for_int(self.value) > self.type.bits:
            raise errors.IntSizeExceeded(self.value)

    @classmethod
    def FromString(cls, location: Location, strval: str):
        int_type, value = parse_int_value(location=location, strval=strval)
        return cls(location=location, type=int_type, value=value)


@dataclass(kw_only=True)
class StrLiteralExpr(LiteralExpr):
    type: StrType
    value: bytes

    def __post_init__(self):
        LiteralExpr.__post_init__(self)
        self.value = self.value.encode('utf-8')


@dataclass(kw_only=True)
class VariantFieldTypeLookupExpr(Expr):
    name: str
