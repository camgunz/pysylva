# pylint: disable=too-many-lines
import enum
import pprint

import lark

# pylint: disable=unused-import
from . import ast, debug, errors

from .location import Location
from .parser import Token, Lark_StandAlone as Parser


_EXPR_NODE_NAMES = [
    'or_expr',
    'and_expr',
    'cmp_expr',
    'bor_expr',
    'bxor_expr',
    'band_expr',
    'shift_expr',
    'arith_expr',
    'mul_expr',
    'inc_dec_expr',
    'unary_expr',
    'power_expr',
    'call_expr',
    'index_expr',
    'move_expr',
    'ref_expr',
    'exref_expr',
    'bool_expr',
    'complex_expr',
    'float_expr',
    'int_expr',
    'rune_expr',
    'array_expr',
    'function_expr',
    'string_expr',
    'struct_expr',
    'carray_expr',
    'cstruct_expr',
    'cunion_expr',
    'lookup_expr'
]


class TypeModifier(enum.Enum):
    Raw = enum.auto()
    Pointer = enum.auto()
    Reference = enum.auto()
    ExclusiveReference = enum.auto()

    @classmethod
    def FromTypeLiteral(cls, type_literal):
        first_child = type_literal.children[0].getText()
        last_child = type_literal.children[-1].getText()

        if first_child == '*':
            return cls.Pointer

        if not first_child == '&':
            return cls.Raw

        if last_child == '!':
            return cls.ExclusiveReference

        return cls.Reference


class ModuleBuilder(lark.Visitor):

    def __init__(self, module, stream):
        self._module = module
        self._stream = stream

    def _handle_expr(self, expr, extra_scope=None):
        debug('_handle_expr', f'{expr}')
        location = Location.FromTree(expr, self._stream)

        if expr.data == 'or_expr':
            pass

        if expr.data == 'and_expr':
            pass

        if expr.data == 'cmp_expr':
            pass

        if expr.data == 'bor_expr':
            pass

        if expr.data == 'bxor_expr':
            pass

        if expr.data == 'band_expr':
            pass

        if expr.data == 'shift_expr':
            pass

        if expr.data == 'arith_expr':
            pass

        if expr.data == 'mul_expr':
            pass

        if expr.data == 'inc_dec_expr':
            pass

        if expr.data == 'unary_expr':
            pass

        if expr.data == 'power_expr':
            pass

        if expr.data == 'call_expr':
            func = expr.children[0]
            args = filter(None, expr.children[1:])
            func_expr = self._handle_expr(func, extra_scope=extra_scope)
            debug('call_expr', f'func_expr: {func_expr}')
            return ast.CallExpr(
                location=location,
                type=func_expr,
                function=func_expr,
                arguments=[
                    self._handle_expr(arg, extra_scope=extra_scope)
                    for arg in args
                ]
            )

        if expr.data == 'index_expr':
            pass

        if expr.data == 'move_expr':
            return ast.MovePointerExpr(
                location=location,
                type=ast.OwnedPointerType(
                    referenced_type=self._get_type(
                        expr.children[0], extra_scope=extra_scope
                    ),
                ),
                expr=self._handle_expr(
                    expr.children[0], extra_scope=extra_scope
                )
            )

        if expr.data == 'ref_expr':
            return ast.ReferencePointerExpr(
                location=location,
                type=ast.ReferencePointerType(
                    referenced_type=self._get_type(
                        expr.children[0], extra_scope=extra_scope
                    ),
                    is_exclusive=False
                ),
                expr=self._handle_expr(
                    expr.children[0], extra_scope=extra_scope
                )
            )

        if expr.data == 'exref_expr':
            return ast.ReferencePointerExpr(
                location=location,
                type=ast.ReferencePointerType(
                    referenced_type=self._get_type(
                        expr.children[0], extra_scope=extra_scope
                    ),
                    is_exclusive=True
                ),
                expr=self._handle_expr(
                    expr.children[0], extra_scope=extra_scope
                )
            )

        if expr.data == 'cpointer_expr':
            referenced_expr = self._handle_expr(
                expr.children[0], extra_scope=extra_scope
            )

            if not isinstance(referenced_expr, ast.BasePointerExpr):
                referenced_type = referenced_expr.type
                referenced_type_is_exclusive = True
            else:
                referenced_type = referenced_expr.referenced_type
                referenced_type_is_exclusive = referenced_expr.is_exclusive

            is_exclusive = len(expr.children) >= 2 and expr.children[1] == '!'

            return ast.CPointerCastExpr(
                location=location,
                type=ast.CPointerType(
                    location=location,
                    referenced_type=referenced_type,
                    referenced_type_is_exclusive=referenced_type_is_exclusive,
                    is_exclusive=is_exclusive
                ),
                expr=referenced_expr
            )

        if expr.data == 'cvoid_expr':
            return ast.CVoidCastExpr(
                location=location,
                expr=self._handle_expr(
                    expr.children[0], extra_scope=extra_scope
                )
            )

        if expr.data == 'bool_expr':
            raw_value = expr.children[0].value
            return ast.BooleanLiteralExpr.FromRawValue(location, raw_value)

        if expr.data == 'complex_expr':
            raw_value = expr.children[0].value
            return ast.ComplexLiteralExpr.FromRawValue(location, raw_value)

        if expr.data == 'float_expr':
            raw_value = expr.children[0].value
            return ast.FloatLiteralExpr.FromRawValue(location, raw_value)

        if expr.data == 'int_expr':
            raw_value = expr.children[0].value
            return ast.IntegerLiteralExpr.FromRawValue(location, raw_value)

        if expr.data == 'rune_expr':
            raw_value = expr.children[0].value
            return ast.RuneLiteralExpr.FromRawValue(location, raw_value)

        if expr.data == 'string_expr':
            raw_value = expr.children[0].value
            return ast.StringLiteralExpr.FromRawValue(location, raw_value)

        if expr.data == 'array_expr':
            pass

        if expr.data == 'struct_expr':
            pass

        if expr.data == 'function_expr':
            pass

        if expr.data == 'lookup_expr':
            name = expr.children.pop(0).value
            value = self._lookup_type(location, name, extra_scope=extra_scope)
            if value is None:
                raise errors.UndefinedSymbol(location, name)

            lookup_expr = ast.LookupExpr(
                location=location, type=value, name=name
            )

            while expr.children:
                debug('lookup', f'_handle_expr expr children: {expr.children}')
                connector_field = expr.children.pop(0)
                reflection = connector_field.value == '::'
                field = expr.children.pop(0)

                if reflection:
                    value = value.reflect(location, field.value)
                    if not value:
                        raise errors.NoSuchField(location, field.value)
                    lookup_expr = ast.ReflectionLookupExpr(
                        location=Location.FromToken(field, self._stream),
                        type=value.type,
                        expr=lookup_expr,
                        name=field.value
                    )
                else:
                    # if value.lookup(location, field.value) is None:
                    #     import pdb
                    #     pdb.set_trace()
                    value = value.lookup(location, field.value)
                    if not value:
                        raise errors.NoSuchField(location, field.value)
                    debug(
                        'lookup',
                        f'_handle_expr: got {value} from {field.value}'
                    )
                    lookup_expr = ast.FieldNameLookupExpr(
                        location=Location.FromToken(field, self._stream),
                        type=value.type,
                        expr=lookup_expr,
                        name=field.value
                    )

            return lookup_expr

    def _handle_stmt(self, stmt):
        return None

    def _process_code_block(self, code_block, extra_scope=None):
        code = []
        extra_scope = extra_scope or {}

        for expr_or_stmt in code_block.children:
            if expr_or_stmt.data in _EXPR_NODE_NAMES:
                code.append(self._handle_expr(expr_or_stmt, extra_scope))
            else:
                code.append(self._handle_stmt(expr_or_stmt))

        return code

    def _lookup_type(
        self, location, type_name, extra_scope=None, deferrable=False
    ):
        # [NOTE] Maybe it's a good idea to have an `UndefinedSymbol` ASTNode?
        #        Or, this could be a general semantic error reporting strategy
        #        where we use the tree to hold errors and report them as we
        #        walk it.
        debug('lookup', f'_lookup looking up {type_name}')
        if extra_scope:
            extra_value = extra_scope.get(type_name)
            if extra_value is not None:
                debug('lookup', f'_lookup returning local {extra_value}')
                return extra_value

        value = self._module.lookup_type(location, type_name)
        if value is None:
            if deferrable:
                return ast.DeferredTypeLookup(location, type_name)
            raise errors.UndefinedSymbol(location, type_name)
        debug('lookup', f'_lookup returning {value}')
        return value

    def _get_type(self, type_obj, extra_scope=None, deferrable=False):
        if isinstance(type_obj, Token):
            loc = Location.FromToken(type_obj, self._stream)
            return self._lookup_type(
                loc,
                type_obj.value,
                extra_scope=extra_scope,
                deferrable=deferrable
            )

        location = Location.FromTree(type_obj, self._stream)

        if type_obj.data == 'c_array_type_expr':
            if len(type_obj.children[0].children) == 3:
                element_count = int(type_obj.children[0].children[2])
            else:
                element_count = None
            return ast.CArrayType(
                location=location,
                element_type=self._get_type(
                    type_obj.children[0].children[0], deferrable=deferrable
                ),
                element_count=element_count
            )

        if type_obj.data == 'c_bit_field_type_expr':
            field_type, field_bit_size = type_obj.children
            return ast.CBitFieldType(
                location=location,
                bits=self._get_type(field_type).bits,
                signed=field_type.startswith('i'),
                field_size=int(field_bit_size)
            )

        if type_obj.data in ('c_function_type_type_expr',
                             'c_block_function_type_type_expr'):
            parameters = []
            for param_obj in type_obj.children[0].children[:-1]:
                name_token, param_type_obj = param_obj.children
                parameters.append(
                    ast.Parameter(
                        location=Location.FromToken(name_token, self._stream),
                        name=name_token.value,
                        type=self._get_type(
                            param_type_obj, deferrable=deferrable
                        )
                    )
                )

            if type_obj.children[0].children[-1] is not None:
                return_type = self._get_type(
                    type_obj.children[0].children[-1].children[0],
                    deferrable=deferrable
                )
            else:
                return_type = None

            if type_obj.data == 'c_function_type_type_expr':
                return ast.CFunctionPointerType(
                    location=location,
                    parameters=parameters,
                    return_type=return_type,
                )
            return ast.CBlockFunctionPointerType(
                location=location,
                parameters=parameters,
                return_type=return_type,
            )

        if type_obj.data == 'c_pointer_type_expr':
            referenced_type_is_exclusive = (
                len(type_obj.children) >= 2 and type_obj.children[1] == '!'
            )
            is_exclusive = (
                len(type_obj.children) >= 3 and type_obj.children[2] == '!'
            )

            return ast.CPointerType(
                location=location,
                referenced_type=self._get_type(
                    type_obj.children[0], deferrable=deferrable
                ),
                referenced_type_is_exclusive=referenced_type_is_exclusive,
                is_exclusive=is_exclusive
            )

        if type_obj.data == 'c_void_type_expr':
            return self._lookup_type(location, 'cvoid', deferrable=deferrable)

        if type_obj.data == 'function_type_expr':
            parameters = []
            for param_obj in type_obj.children[:-1]:
                name_token, param_type_obj = param_obj.children
                parameters.append(
                    ast.Parameter(
                        location=Location.FromToken(name_token, self._stream),
                        name=name_token.value,
                        type=self._get_type(
                            param_type_obj, deferrable=deferrable
                        )
                    )
                )

            if type_obj.children[-1] is not None:
                return_type = self._get_type(
                    type_obj.children[-1], deferrable=deferrable
                )
            else:
                return_type = None

            return ast.FunctionType(
                location=location,
                parameters=parameters,
                return_type=return_type,
            )

        if type_obj.data == 'identifier':
            name = type_obj.children[0]
            return self._lookup_type(location, name, deferrable=deferrable)

        if type_obj.data == 'c_function_type_type_expr':
            parameters = []
            for param_obj in type_obj.children[:-1]:
                name_token, param_type_obj = param_obj.children
                parameters.append(
                    ast.Parameter(
                        location=Location.FromToken(name_token, self._stream),
                        name=name_token.value,
                        type=self._get_type(
                            param_type_obj, deferrable=deferrable
                        )
                    )
                )

            if type_obj.children[-1] is not None:
                return_type = self._get_type(
                    type_obj.children[-1], deferrable=deferrable
                )
            else:
                return_type = None

            return ast.CFunctionType(
                location=location,
                parameters=parameters,
                return_type=return_type,
            )

        if type_obj.data == 'moveparam':
            return ast.OwnedPointerType(
                location=location,
                referenced_type=self._get_type(
                    type_obj.children[0], deferrable=deferrable
                ),
            )

        if type_obj.data == 'refparam':
            return ast.ReferencePointerType(
                location=location,
                referenced_type=self._get_type(
                    type_obj.children[0], deferrable=deferrable
                ),
                is_exclusive=False
            )

        if type_obj.data == 'exrefparam':
            return ast.ReferencePointerType(
                location=location,
                referenced_type=self._get_type(
                    type_obj.children[0], deferrable=deferrable
                ),
                is_exclusive=True
            )

        print(type_obj.pretty())
        print(type(type_obj), type_obj.data)
        raise NotImplementedError

    def alias_def(self, tree):
        self._module.define(
            ast.AliasDef(
                location=Location.FromTree(tree, self._stream),
                name=tree.children[0].value,
                value=self._get_type(tree.children[1])
            )
        )

    def const_def(self, tree):
        self._module.define(
            ast.ConstDef(
                location=Location.FromTree(tree, self._stream),
                name=tree.children[0].value,
                value=self._handle_expr(tree.children[1])
            )
        )

    def c_array_type_def(self, tree):
        if tree.children[1].children[1].value == '*':
            self._module.define(
                ast.CArrayDef(
                    location=Location.FromTree(tree, self._stream),
                    name=tree.children[0].value,
                    type=ast.CArrayType(
                        location=Location.FromTree(tree, self._stream),
                        element_type=self._get_type(
                            tree.children[1].children[0], deferrable=True
                        ),
                        element_count=int(tree.children[1].children[2])
                    )
                )
            )
        else:
            self._module.define(
                ast.CArrayDef(
                    location=Location.FromTree(tree, self._stream),
                    name=tree.children[0].value,
                    type=ast.CArrayType(
                        location=Location.FromTree(tree, self._stream),
                        element_type=self._get_type(
                            tree.children[1].children[0], deferrable=True
                        ),
                        element_count=None
                    )
                )
            )

    def c_function_type_def(self, tree):
        param_objs = tree.children[1].children[:-1]
        return_type_obj = tree.children[1].children[-1]
        parameters = []
        for param_obj in param_objs:
            name_token, param_type_obj = param_obj.children
            parameters.append(
                ast.Parameter(
                    location=Location.FromToken(name_token, self._stream),
                    name=name_token.value,
                    type=self._get_type(param_type_obj)
                )
            )
        if return_type_obj is not None:
            return_type = self._get_type(return_type_obj.children[0])
        else:
            return_type = None

        self._module.define(
            ast.CFunctionDef(
                location=Location.FromTree(tree, self._stream),
                name=tree.children[0].value,
                type=ast.CFunctionType(
                    location=Location.FromTree(tree, self._stream),
                    parameters=parameters,
                    return_type=return_type
                )
            )
        )

    def c_struct_type_def(self, tree):
        fields = []
        for i, field_obj in enumerate(tree.children[1:]):
            name_token, field_type_obj = field_obj.children
            fields.append(
                ast.Field(
                    location=Location.FromToken(name_token, self._stream),
                    name=name_token.value,
                    type=self._get_type(field_type_obj, deferrable=True),
                    index=i,
                )
            )
        self._module.define(
            ast.CStructDef(
                location=Location.FromTree(tree, self._stream),
                name=tree.children[0].value,
                type=ast.CStructType(
                    location=Location.FromTree(tree, self._stream),
                    name=tree.children[0].value,
                    fields=fields
                )
            )
        )

    def c_union_type_def(self, tree):
        fields = []
        for i, field_obj in enumerate(tree.children[1:]):
            name_token, field_type_obj = field_obj.children
            fields.append(
                ast.Field(
                    location=Location.FromToken(name_token, self._stream),
                    name=name_token.value,
                    type=self._get_type(field_type_obj, deferrable=True),
                    index=i
                )
            )
        self._module.define(
            ast.CUnionDef(
                location=Location.FromTree(tree, self._stream),
                name=tree.children[0].value,
                type=ast.CUnionType(
                    location=Location.FromTree(tree, self._stream),
                    fields=fields
                )
            )
        )

    def function_def(self, tree):
        function_type_def, code_block = tree.children
        param_objs = function_type_def.children[1].children[:-1]
        return_type_obj = function_type_def.children[1].children[-1]
        parameters = []
        for param_obj in param_objs:
            name_token, param_type_obj = param_obj.children
            parameters.append(
                ast.Parameter(
                    location=Location.FromToken(name_token, self._stream),
                    name=name_token.value,
                    type=self._get_type(param_type_obj)
                )
            )
        if return_type_obj is not None:
            return_type = self._get_type(return_type_obj.children[0])
        else:
            return_type = None

        scope = {param.name: param.type for param in parameters}

        code = self._process_code_block(code_block, extra_scope=scope)

        self._module.define(
            ast.FunctionDef(
                location=Location.FromTree(tree, self._stream),
                name=function_type_def.children[0].value,
                type=ast.FunctionType(
                    location=Location.FromTree(tree, self._stream),
                    parameters=parameters,
                    return_type=return_type
                ),
                code=code
            )
        )
