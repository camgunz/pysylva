import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors
from .base import Node
from .operator import AttributeLookupMixIn, Operator, ReflectionLookupMixIn
from .sylva_type import LLVMTypeMixIn, SylvaType


@define(eq=False, slots=True)
class Expr(Node, ReflectionLookupMixIn):
    type = field()

    # pylint: disable=no-self-use
    def get_reflection_attribute_type(self, location, name, module):
        from .array import ArrayType
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return ArrayType

    def reflect_attribute(self, location, name, module):
        if name == 'type':
            return self.type
        if name == 'bytes':
            pass


@define(eq=False, slots=True)
class LLVMExprMixIn:

    def emit_llvm_expr(self, module, builder):
        raise NotImplementedError()


@define(eq=False, slots=True)
class LLVMValueExprMixIn(LLVMExprMixIn):
    llvm_value: None | ir.Value

    def emit_llvm_expr(self, module, builder):
        return builder.load(self.llvm_value)


@define(eq=False, slots=True)
class LLVMLiteralExprMixIn(LLVMExprMixIn):
    type: LLVMTypeMixIn
    value: typing.Any

    def emit_llvm_expr(self, module, builder):
        return self.type.get_llvm_type(module)(self.value)


@define(eq=False, slots=True)
class LiteralExpr(Expr, LLVMLiteralExprMixIn):
    value: bool | float | int | str


class ValueExpr(Expr, LLVMValueExprMixIn):
    pass


@define(eq=False, slots=True)
class BaseLookupExpr(Expr, AttributeLookupMixIn, ReflectionLookupMixIn):

    def get_attribute(self, location, name):
        return self.type.get_attribute(location, name)

    def get_reflection_attribute_type(self, location, name, module):
        return self.type.get_reflection_attribute_type(location, name, module)


@define(eq=False, slots=True)
class LookupExpr(BaseLookupExpr):
    name: str


@define(eq=False, slots=True)
class AttributeLookupExpr(BaseLookupExpr):
    expr: Expr
    attribute: str | int
    reflection: bool


@define(eq=False, slots=True)
class FieldIndexLookupExpr(Expr):
    expr: Expr
    index: int

    # def emit(self, builder, name=None):
    #     indices = [self.index]
    #     expr = self.expr # struct, cstruct... array?
    #     while isinstance(expr, FieldIndexLookupExpr):
    #         expr = expr.expr
    #         indices.insert(0, expr.index)
    #     return builder.gep(
    #         self.expr.eval(scope), indices, inbounds=True, name=name
    #     )


@define(eq=False, slots=True)
class ReflectionLookupExpr(Expr):
    expr: Expr
    name: str


@define(eq=False, slots=True)
class CallExpr(LLVMExpr):
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

    def emit_llvm_expr(self, module, builder):
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
    def check_value(self, attribute, operator):
        if operator == '+' and not isinstance(self.expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if operator == '-' and not isinstance(self.expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if operator == '~' and not isinstance(self.expr.type, IntegerType):
            raise errors.InvalidExpressionType(self.location, 'integer')
        if operator == '!' and not isinstance(self.expr.type, BooleanType):
            raise errors.InvalidExpressionType(self.location, 'bool')


@define(eq=False, slots=True)
class BinaryExpr(Expr):
    operator: Operator
    lhs: Expr
    rhs: Expr
