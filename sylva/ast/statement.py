from attrs import define, field

from .base import Node


@define(eq=False, slots=True)
class Stmt(Node):

    def emit(self, module, builder, scope):
        raise NotImplementedError()


@define(eq=False, slots=True)
class StmtBlock(Stmt):
    code = field()


@define(eq=False, slots=True)
class LetStmt(Stmt):
    name = field()
    expr = field()


@define(eq=False, slots=True)
class BreakStmt(Stmt):
    pass


@define(eq=False, slots=True)
class ContinueStmt(Stmt):
    pass


@define(eq=False, slots=True)
class ReturnStmt(Stmt):
    expr = field()


@define(eq=False, slots=True)
class IfStmt(StmtBlock):
    conditional_expr = field()
    else_code = field()


@define(eq=False, slots=True)
class LoopStmt(StmtBlock):
    pass


@define(eq=False, slots=True)
class WhileStmt(StmtBlock):
    conditional_expr = field()
