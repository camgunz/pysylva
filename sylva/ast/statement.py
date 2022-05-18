import typing

from attrs import define

from . import ast


@define(eq=False, slots=True)
class Stmt(ast.ASTNode):
    pass


@define(eq=False, slots=True)
class LetStmt(Stmt):
    name: str
    expr: ast.Expr


@define(eq=False, slots=True)
class StmtBlock(Stmt):
    code: typing.List[ast.Expr | Stmt]


@define(eq=False, slots=True)
class Break(Stmt):
    pass


@define(eq=False, slots=True)
class Continue(Stmt):
    pass


@define(eq=False, slots=True)
class Return(Stmt):
    expr: ast.Expr


@define(eq=False, slots=True)
class If(StmtBlock):
    conditional_expr: ast.Expr
    else_code: typing.List[ast.Expr | Stmt]


@define(eq=False, slots=True)
class Loop(StmtBlock):
    pass


@define(eq=False, slots=True)
class While(StmtBlock):
    conditional_expr: ast.Expr
