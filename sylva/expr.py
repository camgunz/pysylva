from dataclasses import dataclass, field
from typing import Any

from sylva import debug, errors, utils
from sylva.location import Location
from sylva.builtins import (
    BoolType,
    BoolValue,
    CVoidType,
    ComplexType,
    FloatType,
    FloatValue,
    IntType,
    IntValue,
    MonoCPtrType,
    MonoStrType,
    MonoSylvaType,
    MonoVariantType,
    RuneType,
    RuneValue,
    StrValue,
    StringType,
    SylvaObject,
    SylvaType,
    SylvaValue,
)
from sylva.mod import Mod
from sylva.operator import Operator
from sylva.scope import Scope


@dataclass(kw_only=True)
class Expr(SylvaObject):
    location: Location = field(default_factory=Location.Generate)
    type: MonoSylvaType | None = None

    def __post_init__(self):
        if type is None:
            debug('nonetype', f'[{self.location.shorthand}] {type(self)}')

    def eval(self, scopes: Scope | None = None):
        raise NotImplementedError()


@dataclass(kw_only=True)
class LookupExpr(Expr):
    name: str

    def eval(
        self, scopes: Scope | None = None
    ) -> Mod | SylvaType | SylvaValue:
        if scopes:
            val = scopes.lookup(self.name)
            if val is not None:
                return val

        val = self.module.lookup(self.name)
        if val:
            return val

        raise errors.UndefinedSymbol(self.location, self.name)


@dataclass(kw_only=True)
class LiteralExpr(Expr):
    value: Any

    def eval(self, scopes: Scope | None = None):
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

    def eval(self, scopes: Scope | None = None):
        obj = ( # yapf: ignore
            self.obj.eval(scopes)
            if isinstance(self.obj, Expr)
            else self.obj
        )

        member = ( # yapf: ignore
            obj.reflection_lookup(self.name)
            if self.reflection
            else obj.lookup(self.name)
        )

        if member is None:
            raise errors.NoSuchAttribute(self.location, self.name)


@dataclass(kw_only=True)
class CallExpr(Expr):
    function: Expr
    arguments: list[Expr]
    monomorphization_index: int = 0


@dataclass(kw_only=True)
class IndexExpr(Expr):
    obj: Expr
    index_expr: Expr


@dataclass(kw_only=True)
class BoolExpr(Expr):
    type: BoolType


@dataclass(kw_only=True)
class RuneExpr(Expr):
    type: RuneType


@dataclass(kw_only=True)
class ComplexExpr(Expr):
    type: ComplexType


@dataclass(kw_only=True)
class FloatExpr(Expr):
    type: FloatType


@dataclass(kw_only=True)
class IntExpr(Expr):
    type: IntType


@dataclass(kw_only=True)
class StrExpr(Expr):
    type: MonoStrType


@dataclass(kw_only=True)
class StringExpr(Expr):
    type: StringType


@dataclass(kw_only=True)
class CPtrExpr(Expr):
    type: MonoCPtrType
    expr: Expr


@dataclass(kw_only=True)
class CVoidExpr(Expr):
    type: CVoidType
    expr: Expr


@dataclass(kw_only=True)
class VariantExpr(Expr):
    type: MonoVariantType
    expr: CallExpr | IndexExpr | LookupExpr


@dataclass(kw_only=True)
class BoolLiteralExpr(LiteralExpr):
    type: BoolType
    value: BoolValue

    @classmethod
    def FromString(cls, location: Location, module: Mod, strval: str):
        v = BoolValue.FromString(location=location, module=module, s=strval)
        return cls(location=location, module=module, type=v.type, value=v)


@dataclass(kw_only=True)
class RuneLiteralExpr(LiteralExpr):
    type: RuneType
    value: RuneValue

    def __post_init__(self):
        LiteralExpr.__post_init__(self)
        if len(self.value) > 1:
            raise errors.invalidRuneValue('Runes must have len <= 1')

    @classmethod
    def FromString(cls, location: Location, module: Mod, strval: str):
        v = RuneValue.FromString(location=location, module=module, s=strval)
        return cls(location=location, module=module, type=v.type, value=v)


@dataclass(kw_only=True)
class ComplexLiteralExpr(LiteralExpr):
    type: ComplexType
    value: complex

    # @classmethod
    # def FromString(cls, location: Location, strval: str):
    #     # [TODO] Parse complex type literal
    #     int_type, value = parse_int_value(location=location, strval=strval)
    #     return cls(location=location, type=COMPLEX, value=value)


@dataclass(kw_only=True)
class FloatLiteralExpr(LiteralExpr):
    type: FloatType
    value: FloatValue

    @classmethod
    def FromString(cls, location: Location, module: Mod, strval: str):
        v = FloatValue.FromString(location=location, module=module, s=strval)
        return cls(location=location, module=module, type=v.type, value=v)


@dataclass(kw_only=True)
class IntLiteralExpr(LiteralExpr):
    type: IntType
    value: IntValue

    def __post_init__(self):
        LiteralExpr.__post_init__(self)
        if utils.bits_required_for_int(self.value.value) > self.type.bits:
            raise errors.IntSizeExceeded(self.location, self.value.value)

    @classmethod
    def FromString(cls, location: Location, module: Mod, strval: str):
        v = IntValue.FromString(location=location, module=module, s=strval)
        return cls(location=location, module=module, type=v.type, value=v)


@dataclass(kw_only=True)
class StrLiteralExpr(LiteralExpr):
    type: MonoStrType
    value: StrValue

    @classmethod
    def FromString(cls, location: Location, module: Mod, strval: str):
        v = StrValue.FromString(location=location, module=module, s=strval)
        return cls(location=location, module=module, type=v.type, value=v)


@dataclass(kw_only=True)
class VariantFieldTypeLookupExpr(Expr):
    name: str
