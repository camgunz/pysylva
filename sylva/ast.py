import ctypes
import decimal

from functools import cache, cached_property

from llvmlite import ir

from . import errors, types, utils


class ASTNode:

    def __init__(self, location):
        self.location = location

    @property
    def type_name(self):
        return type(self).__name__


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

    def __init__(self, location, type):
        super().__init__(location)
        self.type = type

    # pylint: disable=no-self-use
    def eval(self, location):
        raise errors.ImpossibleCompileTimeEvaluation(location)


class ConstExpr(Expr):

    def __init__(self, location, type, value):
        super().__init__(location, type)
        self.value = value

    def eval(self, location):
        return self.value

    def __repr__(self):
        return f'{self.type_name}(%r, %r, %r)' % (
            self.location, self.type, self.value
        )


class BaseValueExpr(Expr):

    # pylint: disable=unused-argument,no-self-use
    def lookup(self, location, field):
        # raise errors.ImpossibleLookup(location)
        raise errors.ImpossibleCompileTimeEvaluation(location)

    # pylint: disable=unused-argument
    def reflect(self, location, field):
        raise errors.ImpossibleCompileTimeEvaluation(location)
        # if field == 'type':
        #     return self.type
        # if field == 'bytes':
        #     pass
        # raise NotImplementedError()


class Value(BaseValueExpr):

    def __repr__(self):
        return f'{self.type_name}(%r, %r)' % (self.location, self.type)


class ConstValue(ConstExpr, BaseValueExpr):

    # pylint: disable=unused-argument
    def lookup(self, location, field):
        raise NotImplementedError()

        # if isinstance(self.type, types.CStruct):
        #     raise NotImplementedError() # This is a GEP call?
        # if isinstance(self.type, types.CUnion):
        #     raise NotImplementedError() # This is a bitcast and a GEP call?
        # if isinstance(self.type, types.Enum):
        #     raise NotImplementedError() # ???
        # if isinstance(self.type, types.Interface):
        #     raise NotImplementedError() # ???
        # if isinstance(self.type, types.Struct):
        #     raise NotImplementedError() # This is a GEP call?
        # if isinstance(self.type, types.Variant):
        #     raise NotImplementedError() # This is a bitcast and a GEP call?
        # if isinstance(self.type, types.Module):
        #     return self.type.lookup(location, field)

    def reflect(self, location, field):
        if field == 'type':
            return StringLiteral(location, self.type)
        if field == 'bytes':
            pass
        raise NotImplementedError()


class Literal(ConstValue):

    def __repr__(self):
        return f'{type(self).__name__}({repr(self.value)})'

    @cache
    def get_llvm_type(self, module):
        return self.type.get_llvm_type(module)

    @cache
    def get_llvm_value(self, module):
        return self.type.make_constant(module, self.value)


class CVoidCast(ConstExpr):

    def __init__(self, location, expr):
        super().__init__(location, types.Integer(8, signed=True), expr)


class BooleanLiteral(Literal):

    def __init__(self, location, value):
        super().__init__(location, types.Boolean(), value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, raw_value == 'true')

    @cache
    def get_llvm_value(self, module):
        self.type.make_constant(module, 1 if self.value else 0)


class Boolean(Value):

    def __init__(self, location):
        super().__init__(location, types.Boolean())


class RuneLiteral(Literal):

    def __init__(self, location, value):
        super().__init__(location, types.Rune(), value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, raw_value[1:-1])


class Rune(Value):

    def __init__(self, location):
        super().__init__(location, types.Rune())


class StringLiteral(Literal):

    def __init__(self, location, value):
        super().__init__(location, types.String(), value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, raw_value[1:-1])

    @cached_property
    def encoded_data(self):
        # [NOTE] I suppose this is where we'd configure internal string
        #        encoding; easy enough to grab from module.program
        return bytearray(self.value, encoding='utf-8')

    @cache
    def get_llvm_type(self, module):
        return ir.ArrayType(
            types.Integer(8, signed=True).get_llvm_type(module),
            len(self.encoded_data)
        )

    @cache
    def get_llvm_value(self, module):
        self.get_llvm_type(module)(self.encoded_data)

    def reflect(self, location, field):
        if field == 'size':
            value = self.eval(location)
            size = len(bytes(value, encoding='utf-8'))
            return IntegerLiteral.SmallestThatHolds(location, size)
        if field == 'count':
            value = self.eval(location)
            return IntegerLiteral.SmallestThatHolds(location, len(value))


class String(Value):

    def __init__(self, location):
        super().__init__(location, types.String())

    def reflect(self, location, field):
        if field == 'size':
            field_index, field_type = self.type.get_field_info(field)
            return FieldLookupExpr(location, field_type, self, field_index)

        raise NotImplementedError()


class NumericLiteral(Literal):
    pass


class IntegerLiteral(NumericLiteral):

    def __init__(self, location, size, signed, value):
        super().__init__(location, types.Integer(size, signed=signed), value)

    @property
    def signed(self):
        return self.type.signed

    @property
    def size(self):
        return self.type.bits

    @classmethod
    def SmallestThatHolds(cls, location, value):
        size = utils.smallest_uint(value)
        return cls(location, size, signed=False, value=value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
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

        size = size or ctypes.sizeof(ctypes.c_size_t) * 8

        return cls(location, size, signed, value)

    @property
    def type_name(self):
        return f'{"i" if self.signed else "u"}{self.size}'


class Integer(Value):

    def __init__(self, location, size, signed):
        super().__init__(location, types.Integer(size, signed=signed))


class FloatLiteral(NumericLiteral):

    def __init__(self, location, size, value):
        super().__init__(location, types.Float(size), value)

    @property
    def size(self):
        return self.type.bits

    @classmethod
    def FromRawValue(cls, location, raw_value):
        if raw_value.endswith('f16'):
            return cls(location, types.Float(16), float(raw_value[:-3]))
        if raw_value.endswith('f32'):
            return cls(location, types.Float(32), float(raw_value[:-3]))
        if raw_value.endswith('f64'):
            return cls(location, types.Float(64), float(raw_value[:-3]))
        if raw_value.endswith('f128'):
            return cls(location, types.Float(128), float(raw_value[:-4]))
        raise Exception(f'Malformed float value {raw_value}')


class Float(Value):

    def __init__(self, location, size):
        super().__init__(location, types.Float(size))


class ComplexLiteral(NumericLiteral):

    def __init__(self, location, size, value):
        super().__init__(location, types.Complex(size), value)

    @property
    def size(self):
        return self.type.bits

    @classmethod
    def FromRawValue(cls, location, raw_value):
        if raw_value.endswith('c16'):
            return cls(location, types.Complex(16), complex(raw_value[:-3]))
        if raw_value.endswith('c32'):
            return cls(location, types.Complex(32), complex(raw_value[:-3]))
        if raw_value.endswith('c64'):
            return cls(location, types.Complex(64), complex(raw_value[:-3]))
        if raw_value.endswith('c128'):
            return cls(location, types.Complex(128), complex(raw_value[:-4]))
        raise Exception(f'Malformed complex value {raw_value}')


class Complex(Value):

    def __init__(self, location, size):
        super().__init__(location, types.Complex(size))


class DecimalLiteral(NumericLiteral):

    def __init__(self, location, value):
        super().__init__(location, types.Decimal(), value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, decimal.Decimal(raw_value))


class Decimal(Value):

    def __init__(self, location):
        super().__init__(location, types.Decimal())


class Function(Value):

    def __init__(self, location, func_type, code):
        super().__init__(location, func_type.return_type)
        self.func_type = func_type
        self.code = code

    def __repr__(self):
        return 'Function(%r, %r, %r)' % (
            self.location, self.func_type, self.code
        )

    @property
    def parameters(self):
        return self.func_type.parameters

    @property
    def return_type(self):
        return self.func_type.return_type


class Call(Expr):

    def __init__(self, location, function, arguments):
        super().__init__(location, function.return_type)
        self.function = function
        self.arguments = arguments

    def __repr__(self):
        return 'Call(%r, %r)' % (self.function, self.arguments)


class IndexExpr(Expr):

    def __init__(self, location, indexable, index):
        super().__init__(location, indexable.element_type)
        self.indexable = indexable
        self.index = index

    def __repr__(self):
        return 'Index(%r, %r)' % (self.indexable, self.index)


class UnaryExpr(Expr):

    def __init__(self, location, operator, expr):
        super().__init__(location, expr.type)
        self.operator = operator
        self.expr = expr

    def __repr__(self):
        return 'Unary(%r, %r)' % (self.operator, self.expr)


class BinaryExpr(Expr):

    def __init__(self, location, operator, lhs, rhs):
        super().__init__(location, lhs.type)
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self):
        return 'Binary(%r, %r, %r)' % (self.operator, self.lhs, self.rhs)


class FieldLookupExpr(Expr):

    def __init__(self, location, type, object, index):
        super().__init__(location, type)
        self.object = object
        self.index = index

    def __repr__(self):
        return 'FieldLookup(%r, %r)' % (self.object, self.index)


class SingleLookupExpr(Expr):

    def __init__(self, location, type, name):
        super().__init__(location, type) # [FIXME] I think?
        self.name = name

    def __repr__(self):
        return 'SingleLookup(%r)' % (self.name)


class LookupExpr(Expr):

    def __init__(self, location, type, namespace, name, reflection=False):
        super().__init__(location, type) # [FIXME] I think?
        self.namespace = namespace
        self.name = name
        self.reflection = reflection

    def __repr__(self):
        return 'Lookup(%r, %r, reflection=%r)' % (
            self.namespace, self.name, self.reflection
        )


class Move(ConstValue):

    def __init__(self, location, value):
        super().__init__(
            location, types.OwnedPointer(location, value.type), value
        )

    def __repr__(self):
        return 'Move(%r)' % (self.value)


class Pointer(Value):

    def __repr__(self):
        return '%s(%r)' % (self.type_name, self.type)

    @property
    def referenced_type(self):
        return self.type.referenced_type

    @property
    def is_exclusive(self):
        return self.type.is_exclusive

    def deref(self, location):
        return self.referenced_type.get_value(location)


class Reference(Pointer):

    def __init__(self, location, referenced_type, is_exclusive):
        super().__init__(
            location,
            types.ReferencePointer(location, referenced_type, is_exclusive)
        )


class OwnedPointer(Pointer):

    def __init__(self, location, referenced_type):
        super().__init__(
            location, types.OwnedPointer(location, referenced_type)
        )


class CPointer(Pointer):

    def __init__(
        self,
        location,
        referenced_type,
        referenced_type_is_exclusive,
        is_exclusive
    ):
        super().__init__(
            location,
            types.CPtr(
                location,
                referenced_type,
                referenced_type_is_exclusive,
                is_exclusive
            )
        )


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
