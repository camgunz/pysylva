from .base import Node


class Stmt(Node):

    def emit(self, module, builder, scope):
        raise NotImplementedError()


class StmtBlock(Stmt):

    def __init__(self, location, code):
        Stmt.__init__(self, location)
        self.code = code


class LetStmt(Stmt):

    def __init__(self, location, name, expr):
        Stmt.__init__(self, location)
        self.name = name
        self.expr = expr

    def emit(self, module, builder, scope):
        value = self.expr.emit(module, builder, scope)
        return builder.store(value, self.name)


class AssignStmt(Stmt):

    def __init__(self, location, name, expr):
        Stmt.__init__(self, location)
        self.name = name
        self.expr = expr

    def emit(self, module, builder, scope):
        value = self.expr.emit(module, builder, scope)
        return builder.store(value, self.name)


class BreakStmt(Stmt):
    pass


class ContinueStmt(Stmt):
    pass


class ReturnStmt(Stmt):

    def __init__(self, location, expr):
        Stmt.__init__(self, location)
        self.expr = expr


class IfStmt(StmtBlock):

    def __init__(self, location, code, conditional_expr, else_code):
        StmtBlock.__init__(self, location, code)
        self.conditional_expr = conditional_expr
        self.else_code = else_code


class LoopStmt(StmtBlock):
    pass


class WhileStmt(StmtBlock):

    def __init__(self, location, code, conditional_expr):
        StmtBlock.__init__(self, location, code)
        self.conditional_expr = conditional_expr
