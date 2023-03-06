from dataclasses import dataclass
from typing import Any, Union

from sylva import errors
from sylva.builtins import (
    BoolType,
    ComplexType,
    FloatType,
    IntType,
    MonoCArrayType,
    RuneType,
    StrType,
    SylvaDef,
    SylvaType,
    SylvaValue,
)
from sylva.expr import Expr


@dataclass(kw_only=True)
class ConstExpr(Expr):

    def eval(self, module):
        raise NotImplementedError()


@dataclass(kw_only=True)
class ConstLookupExpr(ConstExpr):
    name: str

    def eval(self, module):
        val = module.lookup(self.name)
        if val is None:
            raise errors.UndefinedSymbol(self.location, self.name)
        return val


@dataclass(kw_only=True)
class ConstLiteralExpr(ConstExpr):
    value: Any

    def eval(self, module):
        return self.value


@dataclass(kw_only=True)
class ConstAttributeLookupExpr(ConstExpr):
    name: str
    obj: SylvaValue


@dataclass(kw_only=True)
class ConstReflectionLookupExpr(ConstExpr):
    name: str
    obj: SylvaValue


@dataclass(kw_only=True)
class ConstTypeLiteralExpr(ConstExpr):
    value: SylvaType

    def eval(self, module):
        return self.value


@dataclass(kw_only=True)
class ConstTypeExpr(ConstExpr):
    expr: ConstExpr
    type: SylvaType

    def eval(self, module):
        return self.expr.eval(module)


@dataclass(kw_only=True)
class ConstDef(SylvaDef):
    pass


@dataclass(kw_only=True)
class NumericConstLiteralExpr(ConstLiteralExpr):
    type: Union[ComplexType, FloatType, IntType]

    @property
    def size(self):
        return self.type.bits


@dataclass(kw_only=True)
class IntConstLiteralExpr(NumericConstLiteralExpr):
    type: IntType

    @property
    def signed(self):
        return self.type.signed


@dataclass(kw_only=True)
class FloatConstLiteralExpr(NumericConstLiteralExpr):
    type: FloatType


@dataclass(kw_only=True)
class ComplexConstLiteralExpr(NumericConstLiteralExpr):
    type: ComplexType


@dataclass(kw_only=True)
class BoolConstLiteralExpr(ConstLiteralExpr):
    type: BoolType


@dataclass(kw_only=True)
class CArrayTypeLiteralExpr(ConstLiteralExpr):
    type: MonoCArrayType


@dataclass(kw_only=True)
class CStrLiteralExpr(ConstLiteralExpr):
    pass


@dataclass(kw_only=True)
class CVoidExpr(Expr):
    is_exclusive: bool = False

    def __init__(self, location, is_exclusive=False):
        from .type_singleton import TypeSingletons

        Expr.__init__(self, location=location, type=TypeSingletons.CVOID)
        self.is_exclusive = is_exclusive


@dataclass(kw_only=True)
class RuneConstLiteralExpr(ConstLiteralExpr):
    type: RuneType


@dataclass(kw_only=True)
class StrConstLiteralExpr(ConstLiteralExpr):
    type: StrType
