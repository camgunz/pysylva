import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors
from .base import Node
from .bool import BoolType
from .operator import Operator
from .number import IntType, NumericType
from .reflection_lookup import ReflectionLookupMixIn
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class Expr(Node, ReflectionLookupMixIn):
    type = field()

    # pylint: disable=no-self-use
    def get_reflection_attribute_type(self, location, name):
        from .array import ArrayType
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return ArrayType

    def reflect_attribute(self, location, name):
        if name == 'type':
            return self.type
        if name == 'bytes':
            pass

    def emit(self, module, builder):
        raise NotImplementedError()


@define(eq=False, slots=True)
class ValueExpr(Expr):
    llvm_value: None | ir.Value

    def emit(self, module, builder):
        return builder.load(self.llvm_value)


@define(eq=False, slots=True)
class LiteralExpr(Expr):
    type: SylvaType
    value: bool | float | int | str

    def emit(self, module, builder):
        return self.type.llvm_type(self.value)


@define(eq=False, slots=True)
class CallExpr(Expr):
    function: Expr
    arguments: typing.List[Expr]
    monomorphization_index: int | None = None
    llvm_function: ir.Function | None = None
    llvm_arguments: typing.List[ir.Value] | None = None

    @classmethod
    def Def(
        cls, location, type, function, arguments, monomorphization_index=0
    ):
        return cls(
            location=location,
            type=type,
            function=function,
            arguments=arguments,
            monomorphization_index=monomorphization_index
        )

    def emit(self, module, builder):
        return builder.call(
            self.llvm_function, self.llvm_arguments, cconv='fastcc'
        )


@define(eq=False, slots=True)
class IndexExpr(Expr):
    indexable: Expr
    index: Expr


@define(eq=False, slots=True)
class UnaryExpr(Expr):
    operator: str = field()
    expr: Expr

    # pylint: disable=unused-argument
    @operator.validator
    def check_value(self, attribute, op):
        if op == '+' and not isinstance(self.expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if op == '-' and not isinstance(self.expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if op == '~' and not isinstance(self.expr.type, IntType):
            raise errors.InvalidExpressionType(self.location, 'integer')
        if op == '!' and not isinstance(self.expr.type, BoolType):
            raise errors.InvalidExpressionType(self.location, 'bool')


@define(eq=False, slots=True)
class BinaryExpr(Expr):
    operator: Operator
    lhs: Expr
    rhs: Expr
