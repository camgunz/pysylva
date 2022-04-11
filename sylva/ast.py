import ctypes
import decimal

from functools import cache, cached_property

from llvmlite import ir

from . import types


class ASTNode:

    def __init__(self, location):
        self.location = location


class Decl(ASTNode):
    pass


class ModuleDecl(Decl):

    def __init__(self, location, name):
        super().__init__(location)
        self.name = name


class RequirementDecl(Decl):

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
        return f'{type(self).__name__}({repr(self.value)})'

    @property
    def type_name(self):
        raise NotImplementedError()

    @cache
    def get_type(self, module):
        return module.lookup(self.type_name)

    @cache
    def get_llvm_type(self, module):
        return self.get_type(module).get_llvm_type(module)

    @cache
    def get_llvm_value(self, module):
        return self.get_type(module).make_constant(module, self.value)


class BooleanLiteralExpr(LiteralExpr):

    def __init__(self, location, raw_value):
        super().__init__(location, raw_value, raw_value == 'true')

    @property
    def type_name(self):
        return 'bool'

    @cache
    def get_llvm_value(self, module):
        self.get_type(module).make_constant(module, 1 if self.value else 0)


class RuneLiteralExpr(LiteralExpr):

    def __init__(self, location, raw_value):
        super().__init__(location, raw_value, raw_value[1:-1])

    @property
    def type_name(self):
        return 'rune'


class StringLiteralExpr(LiteralExpr):

    def __init__(self, location, raw_value):
        super().__init__(location, raw_value, raw_value[1:-1])

    @cached_property
    def encoded_data(self):
        # [NOTE] I suppose this is where we'd configure internal string
        #        encoding; easy enough to grab from module.program
        return bytearray(self.value, encoding='utf-8')

    @property
    def type_name(self):
        return 'str'

    @cache
    def get_llvm_type(self, module):
        return ir.ArrayType(
            types.Integer(8, signed=True).get_llvm_type(module),
            len(self.encoded_data)
        )

    @cache
    def get_llvm_value(self, module):
        self.get_llvm_type(module)(self.encoded_data)


class NumericLiteralExpr(LiteralExpr):
    pass


class IntegerLiteralExpr(NumericLiteralExpr):

    def __init__(self, location, raw_value):
        self.signed, self.given_size, value = self._parse_raw_value(raw_value)
        self.size = self.given_size or ctypes.sizeof(ctypes.c_size_t) * 8
        super().__init__(location, raw_value, value)

    @staticmethod
    def _parse_raw_value(raw_value):
        if raw_value.startswith('0b') or raw_value.startswith('0B'):
            base = 2
        elif raw_value.startswith('0o') or raw_value.startswith('0O'):
            base = 8
        elif raw_value.startswith('0x') or raw_value.startswith('0X'):
            base = 16
        else:
            base = 10

        if raw_value.endswith('i'):
            signed, size, value = True, None, int(raw_value[:-1], base)
        elif raw_value.endswith('i8'):
            signed, size, value = True, 8, int(raw_value[:-2], base)
        elif raw_value.endswith('i16'):
            signed, size, value = True, 16, int(raw_value[:-3], base)
        elif raw_value.endswith('i32'):
            signed, size, value = True, 32, int(raw_value[:-3], base)
        elif raw_value.endswith('i64'):
            signed, size, value = True, 64, int(raw_value[:-3], base)
        elif raw_value.endswith('i128'):
            signed, size, value = True, 128, int(raw_value[:-4], base)
        elif raw_value.endswith('u'):
            signed, size, value = False, None, int(raw_value[:-1], base)
        elif raw_value.endswith('u8'):
            signed, size, value = False, 8, int(raw_value[:-2], base)
        elif raw_value.endswith('u16'):
            signed, size, value = False, 16, int(raw_value[:-3], base)
        elif raw_value.endswith('u32'):
            signed, size, value = False, 32, int(raw_value[:-3], base)
        elif raw_value.endswith('u64'):
            signed, size, value = False, 64, int(raw_value[:-3], base)
        elif raw_value.endswith('u128'):
            signed, size, value = False, 128, int(raw_value[:-4], base)
        else: # [NOTE] Warn here?
            signed, size = False, None

        return signed, size or ctypes.sizeof(ctypes.c_size_t) * 8, value

    @property
    def type_name(self):
        return f'{"i" if self.signed else "u"}{self.size}'


class FloatLiteralExpr(NumericLiteralExpr):

    def __init__(self, location, raw_value):
        self.size, value = self._parse_raw_value(raw_value)
        super().__init__(location, raw_value, value)

    @staticmethod
    def _parse_raw_value(raw_value):
        if raw_value.endswith('f16'):
            return 16, float(raw_value[:-3])
        if raw_value.endswith('f32'):
            return 32, float(raw_value[:-3])
        if raw_value.endswith('f64'):
            return 64, float(raw_value[:-3])
        if raw_value.endswith('f128'):
            return 128, float(raw_value[:-4])
        raise Exception(f'Malformed float value {raw_value}')


class DecimalLiteralExpr(NumericLiteralExpr):

    def __init__(self, location, raw_value):
        super().__init__(location, raw_value, decimal.Decimal(raw_value))


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


class SingleLookupExpr(Expr):

    def __init__(self, location, name):
        super().__init__(location)
        self.name = name

    def __repr__(self):
        return 'SingleLookup(%r)' % (self.name)


class LookupExpr(Expr):

    def __init__(self, location, namespace, name, reflection=False):
        super().__init__(location)
        self.namespace = namespace
        self.name = name
        self.reflection = reflection

    def __repr__(self):
        return 'Lookup(%r, %r, reflection=%r)' % (
            self.namespace, self.name, self.reflection
        )


class LookupNameExpr(Expr):

    def __init__(self, location, name):
        super().__init__(location)
        self.name = name

    def __repr__(self):
        return 'LookupName(%r)' % (self.name)


class DeferredLookup(ASTNode):

    def __init__(self, location, value):
        super().__init__(location)
        self.value = value

    def __repr__(self):
        return 'DeferredLookup(%r)' % (self.value)


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
