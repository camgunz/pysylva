class ASTNode:

    def __init__(self, location):
        self.location = location


class Stmt(ASTNode):
    pass


class ModuleStmt(Stmt):

    def __init__(self, location, name):
        super().__init__(location)
        self.name = name


class RequirementStmt(Stmt):

    def __init__(self, location, name):
        super().__init__(location)
        self.name = name


class Expr(ASTNode):
    pass


class LiteralExpr(Expr):

    def __init__(self, location, raw_value, value):
        super().__init__(location)
        self.raw_value = raw_value
        self.value = value

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.value)}'


class BooleanLiteralExpr(LiteralExpr):
    pass


class RuneLiteralExpr(LiteralExpr):
    pass


class StringLiteralExpr(LiteralExpr):
    pass


class NumericLiteralExpr(LiteralExpr):
    pass


class IntegerLiteralExpr(NumericLiteralExpr):

    def __init__(self, location, raw_value, value, signed, size, overflow):
        super().__init__(location, raw_value, value)
        self.signed = signed
        self.size = size
        self.overflow = overflow


class FloatLiteralExpr(NumericLiteralExpr):

    def __init__(self, location, raw_value, value, size, round):
        super().__init__(location, raw_value, value)
        self.size = size
        self.round = round


class DecimalLiteralExpr(NumericLiteralExpr):

    def __init__(self, location, raw_value, value, round):
        super().__init__(location, raw_value, value)
        self.round = round


class CallExpr(Expr):

    def __init__(self, location, function, arguments):
        super().__init__(location)
        self.function = function
        self.arguments = arguments

    def __repr__(self):
        return 'Call(%r, %r)' % (self.function, self.arguments)


class IndexExpr(Expr):

    def __init__(self, location, indexable, index):
        super().__init__(location)
        self.indexable = indexable
        self.index = index

    def __repr__(self):
        return 'Index(%r, %r)' % (self.indexable, self.index)


class UnaryExpr(Expr):

    def __init__(self, location, operator, expr):
        super().__init__(location)
        self.operator = operator
        self.expr = expr

    def __repr__(self):
        return 'Unary(%r, %r)' % (self.operator, self.expr)


class BinaryExpr(Expr):

    def __init__(self, location, operator, lhs, rhs):
        super().__init__(location)
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return 'Binary(%r, %r, %r)' % (self.operator, self.lhs, self.rhs)


class LookupExpr(Expr):

    def __init__(self, location, identifier):
        super().__init__(location)
        self.identifier = identifier

    def __repr__(self):
        return 'Lookup(%r)' % (self.identifier)


class Interface(ASTNode):

    def __init__(self, location, func_types=None, funcs=None):
        super().__init__(location)
        self.location = location
        self.func_types = func_types or []
        self.funcs = funcs or []
        self.implementing_types = {}

    def __repr__(self):
        return 'Interface(%r, %r, %r)' % (
            self.location, self.func_types, self.funcs
        )


class Implementation(ASTNode):

    def __init__(self, location, interface, implementing_type, funcs):
        super().__init__(location)
        self.interface = interface
        self.implementing_type = implementing_type
        self.funcs = funcs

    def __repr__(self):
        return 'Implementation(%r, %r, %r, %r)' % (
            self.location, self.interface, self.implementing_type, self.funcs
        )


class DeferredLookup(ASTNode):

    def __init__(self, location, value):
        super().__init__(location)
        self.value = value

    def __repr__(self):
        return 'DeferredLookup(%r, %r)' % (self.location, self.value)


class If(ASTNode):

    def __init__(self, location, conditional_expr, code):
        super().__init__(location)
        self.conditional_expr = conditional_expr
        self.code = code


class Else(ASTNode):

    def __init__(self, location, block):
        super().__init__(location)
        self.block = block


class Loop(ASTNode):

    def __init__(self, location, code):
        super().__init__(location)
        self.code = code


class While(ASTNode):

    def __init__(self, location, conditional_expr, code):
        super().__init__(location)
        self.conditional_expr = conditional_expr
        self.code = code


class Break(ASTNode):
    pass


class Continue(ASTNode):
    pass


class Return(ASTNode):

    def __init__(self, location, expr):
        super().__init__(location)
        self.expr = expr
