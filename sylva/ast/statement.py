import typing

from attrs import define

from .base import Node
from .expr import Expr


@define(eq=False, slots=True)
class Stmt(Node):
    pass


@define(eq=False, slots=True)
class StmtBlock(Stmt):
    code: typing.List[Expr | Stmt]


@define(eq=False, slots=True)
class LetStmt(Stmt):
    name: str
    expr: Expr


@define(eq=False, slots=True)
class BreakStmt(Stmt):
    pass


@define(eq=False, slots=True)
class ContinueStmt(Stmt):
    pass


@define(eq=False, slots=True)
class ReturnStmt(Stmt):
    expr: Expr


@define(eq=False, slots=True)
class IfStmt(StmtBlock):
    conditional_expr: Expr
    else_code: typing.List[Expr | Stmt]


@define(eq=False, slots=True)
class LoopStmt(StmtBlock):
    pass


@define(eq=False, slots=True)
class WhileStmt(StmtBlock):
    conditional_expr: Expr
