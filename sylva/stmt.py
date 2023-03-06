from dataclasses import dataclass, field
from typing import Union

from sylva.expr import Expr
from sylva.builtins import SylvaObject


@dataclass(kw_only=True)
class Stmt(SylvaObject):

    def emit(self, obj, module, builder, scope, name):
        raise NotImplementedError()


@dataclass(kw_only=True)
class StmtBlock(Stmt):
    code: list[Union[Expr | Stmt]] = field(default_factory=list)


@dataclass(kw_only=True)
class LetStmt(Stmt):
    name: str
    expr: Expr


@dataclass(kw_only=True)
class AssignStmt(Stmt):
    name: str
    expr: Expr


@dataclass(kw_only=True)
class BreakStmt(Stmt):
    pass


@dataclass(kw_only=True)
class ContinueStmt(Stmt):
    pass


@dataclass(kw_only=True)
class ReturnStmt(Stmt):
    expr: Expr


@dataclass(kw_only=True)
class IfStmt(StmtBlock):
    conditional_expr: Expr
    else_code: list[Union[Expr | Stmt]] = field(default_factory=list)


@dataclass(kw_only=True)
class LoopStmt(StmtBlock):
    pass


@dataclass(kw_only=True)
class WhileStmt(StmtBlock):
    conditional_expr: Expr
