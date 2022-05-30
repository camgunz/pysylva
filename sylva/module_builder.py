import enum

import lark

from . import ast, debug, errors

from .location import Location


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

    # [TODO] Save parameterization info in the module.
    # [TODO] Add argument scope requirements to functions at assignment sites
    # [TODO] Add variable scope type info to variables at definition sites
    # [TODO] Check that impl funcs match iface funcs
    # [TODO] Check that call argument types match function parameter types
    # [TODO] Check that assignment rvalues match lvalues

    def __init__(self, module, stream):
        super().__init__()
        self._module = module
        self._stream = stream

    # pylint: disable=too-many-locals
    def _handle_expr(self, expr, scope):
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
            ex = self._handle_expr(expr.children[1], scope)

            return ast.UnaryExpr(
                location=Location.FromTree(expr, self._stream),
                type=ex.type,
                operator=expr.children[0].value,
                expr=ex,
            )

        if expr.data == 'power_expr':
            pass

        if expr.data == 'call_expr':
            func = expr.children[0]
            args = filter(None, expr.children[1:])
            func_expr = self._handle_expr(func, scope)
            debug('call_expr', f'func_expr: {func_expr}')
            argument_exprs = []
            for arg in args:
                # [TODO] save parameterization info in the module
                argument_expr = self._handle_expr(arg, scope)
                argument_exprs.append(argument_expr)

            debug('funcmono', f'arg exprs: {argument_exprs}')

            if isinstance(func_expr, ast.AttributeLookupExpr):
                ale = func_expr
                while isinstance(ale.obj, ast.AttributeLookupExpr):
                    ale = func_expr.expr
                func_type = ale.type
            elif isinstance(func_expr, ast.AttributeLookupExpr):
                func_type = func_expr.type
            else:
                raise Exception(
                    'Can\'t figure out how to get a function type from '
                    f'{func_expr}'
                )

            if not isinstance(func_type, (ast.FnType, ast.CFnType)):
                # [FIXME] Make this an actual semantic Sylva error to try and
                #         call something that isn't a function
                raise Exception(
                    f'Got non-function-type from {func_expr}\n'
                    f'{func_type}'
                )

            return ast.CallExpr(
                location=location,
                function=func_expr,
                arguments=argument_exprs
            )

        if expr.data == 'index_expr':
            pass

        if expr.data == 'move_expr':
            return ast.PointerExpr(
                location=location,
                expr=self._handle_expr(expr.children[0], scope),
                is_reference=False,
                is_exclusive=True
            )

        if expr.data == 'ref_expr':
            return ast.PointerExpr(
                location=location,
                expr=self._handle_expr(expr.children[0], scope),
                is_reference=False,
                is_exclusive=True
            )

        if expr.data == 'exref_expr':
            return ast.PointerExpr(
                location=location,
                expr=self._handle_expr(expr.children[0], scope),
                is_reference=True,
                is_exclusive=True
            )

        if expr.data == 'cpointer_expr':
            referenced_expr = self._handle_expr(expr.children[0], scope)

            if isinstance(referenced_expr, ast.PointerExpr):
                # `cptr` acts as a cast on pointer expressions; we implement
                # that by stripping off a pointer expr
                expr = referenced_expr.expr
                referenced_type_is_exclusive = expr.is_exclusive
            else:
                # otherwise we treat this an exclusive pointer
                referenced_type_is_exclusive = True

            is_exclusive = len(expr.children) >= 2 and expr.children[1] == '!'

            return ast.CPtrExpr(
                location=location,
                expr=referenced_expr,
                is_exclusive=is_exclusive,
                referenced_type_is_exclusive=referenced_type_is_exclusive,
            )

        if expr.data == 'cvoid_expr':
            return ast.CVoidExpr(
                location=location,
                expr=self._handle_expr(expr.children[0], scope)
            )

        if expr.data == 'bool_expr':
            raw_value = expr.children[0].value
            return ast.BoolLiteralExpr(location, raw_value == 'true')

        if expr.data == 'complex_expr':
            raw_value = expr.children[0].value
            return ast.ComplexLiteralExpr.FromRawValue(location, raw_value)

        if expr.data == 'float_expr':
            raw_value = expr.children[0].value
            return ast.FloatLiteralExpr.FromRawValue(location, raw_value)

        if expr.data == 'int_expr':
            raw_value = expr.children[0].value
            return ast.IntLiteralExpr.FromRawValue(location, raw_value)

        if expr.data == 'rune_expr':
            raw_value = expr.children[0].value
            return ast.RuneLiteralExpr(location, raw_value[1:-1])

        if expr.data == 'string_expr':
            raw_value = expr.children[0].value
            return ast.StrLiteralExpr(
                location, bytearray(raw_value[1:-1], encoding='utf-8')
            )

        if expr.data == 'array_expr':
            pass

        if expr.data == 'struct_expr':
            pass

        if expr.data == 'function_expr':
            pass

        if expr.data == 'lookup_expr':
            name = expr.children.pop(0).value
            value = scope.get(name)
            if value is not None:
                debug(
                    'lookup',
                    f'_handle_expr found first lookup ({value}) in scope'
                )
            else:
                attr = self._module.get_attribute(name)
                if attr is None:
                    raise errors.UndefinedSymbol(location, name)
                value = attr.emit(None, self._module, None, scope, None)

            debug('lookup', f'_handle_expr starting lookup on {name} {value}')
            lookup_expr = ast.LookupExpr(
                location=location, type=value, name=name
            )

            while expr.children:
                debug('lookup', f'_handle_expr looking up {name} on {value}')
                reflection = expr.children.pop(0).value == '::'
                attribute_token = expr.children.pop(0)
                location = Location.FromToken(attribute_token, self._stream)

                if reflection:
                    value = value.get_reflection_attribute(
                        attribute_token.value
                    )
                    if value is None:
                        raise errors.NoSuchAttribute(
                            location, attribute_token.value
                        )

                    lookup_expr = ast.ReflectionLookupExpr(
                        location=location,
                        type=value.type,
                        name=attribute_token.value,
                        obj=lookup_expr,
                    )
                else:
                    value = value.get_attribute(attribute_token.value)
                    if value is None:
                        raise errors.NoSuchAttribute(
                            location, attribute_token.value
                        )

                    lookup_expr = ast.AttributeLookupExpr(
                        location=location,
                        type=value.type,
                        name=attribute_token.value,
                        obj=lookup_expr,
                    )

            return lookup_expr

    def _handle_stmt(self, stmt, scope):
        location = Location.FromTree(stmt, stream=self._stream)
        if stmt.data == 'let_stmt':
            name = stmt.children[0].value
            name_location = Location.FromToken(stmt.children[0], self._stream)

            existing_value = self._lookup(name, scope=scope)
            if existing_value is not None:
                location = existing_value.location
                raise errors.DuplicateDefinition(name, name_location, location)

            expr = self._handle_expr(stmt.children[1], scope)

            scope[name] = expr
            return ast.LetStmt(location, name, expr)

    def _process_code_block(self, code_block, scope=None):
        code = []
        local_scope = {}
        if scope is not None:
            local_scope.update(scope)

        for expr_or_stmt in code_block.children:
            if expr_or_stmt.data in _EXPR_NODE_NAMES:
                code.append(self._handle_expr(expr_or_stmt, local_scope))
            else:
                code.append(self._handle_stmt(expr_or_stmt, local_scope))

        return code

    def _lookup(self, name, scope=None):
        # [NOTE] Maybe it's a good idea to have an `UndefinedSymbol` ASTNode?
        #        Or, this could be a general semantic error reporting strategy
        #        where we use the tree to hold errors and report them as we
        #        walk it.
        debug('lookup', f'_lookup looking up {name}')
        if scope:
            value = scope.get(name)
            if value is not None:
                debug('lookup', f'_lookup returning local {value}')
                return value

        return self._module.get_attribute(name)

    def _get_type(
        self, type_obj, scope=None, accept_missing=False, outer_types=None
    ):
        if isinstance(type_obj, lark.lexer.Token):
            location = Location.FromToken(type_obj, self._stream)
            type = self._lookup(type_obj.value, scope=scope)

            if type is not None:
                return type.type

            if not accept_missing:
                raise errors.UndefinedSymbol(location, type_obj.value)

            return type

        location = Location.FromTree(type_obj, self._stream)

        if type_obj.data == 'identifier':
            name = type_obj.children[0]
            type = self._lookup(name, scope=scope)

            if type is not None:
                return type.type

            if not accept_missing:
                raise errors.UndefinedSymbol(location, name)

            return type

        if type_obj.data == 'c_array_type_expr':
            element_count = int(type_obj.children[0].children[1])
            return ast.TypeSingletons.ARRAY.get_or_create_monomorphization(
                location=location,
                element_type=self._get_type(
                    type_obj.children[0].children[0],
                    accept_missing=accept_missing
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

        if type_obj.data in ('c_function_type_expr',
                             'c_block_function_type_expr'):
            parameters = []
            for param_obj in type_obj.children[0].children[:-1]:
                name_token, param_type_obj = param_obj.children
                parameters.append(
                    ast.Parameter(
                        location=Location.FromToken(name_token, self._stream),
                        name=name_token.value,
                        type=self._get_type(
                            param_type_obj, accept_missing=accept_missing
                        ),
                    )
                )

            if type_obj.children[0].children[-1] is not None:
                return_type = self._get_type(
                    type_obj.children[0].children[-1].children[0],
                    accept_missing=accept_missing
                )
            else:
                return_type = None

            if type_obj.data == 'c_function_type_expr':
                return ast.CFnPointerType(
                    location=location,
                    parameters=parameters,
                    return_type=return_type,
                )
            return ast.CBlockFnPointerType(
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

            referenced_type_name = type_obj.children[0]

            referenced_type = None

            if outer_types:
                referenced_type = outer_types.get(referenced_type_name)

            if referenced_type is None:
                referenced_type = self._get_type(type_obj.children[0])

            return ast.TypeSingletons.CPTR.get_or_create_monomorphization(
                location=location,
                referenced_type=referenced_type,
                is_exclusive=is_exclusive,
                referenced_type_is_exclusive=referenced_type_is_exclusive
            )

        if type_obj.data == 'c_void_type_expr':
            return ast.TypeSingletons.CVOID

        if type_obj.data == 'function_type_expr':
            parameters = []
            for param_obj in type_obj.children[:-1]:
                name_token, param_type_obj = param_obj.children
                parameters.append(
                    ast.Parameter(
                        location=Location.FromToken(name_token, self._stream),
                        name=name_token.value,
                        type=self._get_type(
                            param_type_obj, accept_missing=accept_missing
                        ),
                    )
                )

            if type_obj.children[-1] is not None:
                return_type = self._get_type(
                    type_obj.children[-1], accept_missing=accept_missing
                )
            else:
                return_type = None

            return ast.FnType(
                location=location,
                monomorphizations=[
                    ast.MonoFnType(
                        location=location,
                        parameters=parameters,
                        return_type=return_type
                    )
                ]
            )

        if type_obj.data == 'c_function_type_expr':
            parameters = []
            for param_obj in type_obj.children[:-1]:
                name_token, param_type_obj = param_obj.children
                parameters.append(
                    ast.Parameter(
                        location=Location.FromToken(name_token, self._stream),
                        name=name_token.value,
                        type=self._get_type(
                            param_type_obj, accept_missing=accept_missing
                        ),
                    )
                )

            if type_obj.children[-1] is not None:
                return_type = self._get_type(
                    type_obj.children[-1], accept_missing=accept_missing
                )
            else:
                return_type = None

            return ast.CFnType(
                location=location,
                parameters=parameters,
                return_type=return_type,
            )

        if type_obj.data == 'moveparam':
            return ast.TypeSingletons.POINTER.get_or_create_monomorphization(
                location=location,
                referenced_type=self._get_type(
                    type_obj.children[0], accept_missing=accept_missing
                ),
                is_reference=False,
                is_exclusive=True
            )

        if type_obj.data == 'refparam':
            return ast.TypeSingletons.POINTER.get_or_create_monomorphization(
                location=location,
                referenced_type=self._get_type(
                    type_obj.children[0], accept_missing=accept_missing
                ),
                is_reference=True,
                is_exclusive=False
            )

        if type_obj.data == 'exrefparam':
            return ast.TypeSingletons.POINTER.get_or_create_monomorphization(
                location=location,
                referenced_type=self._get_type(
                    type_obj.children[0], accept_missing=accept_missing
                ),
                is_reference=True,
                is_exclusive=True
            )

        print(type_obj.pretty())
        print(type(type_obj), type_obj.data)
        raise NotImplementedError

    def alias_def(self, tree):
        ad = ast.Alias(
            location=Location.FromTree(tree, self._stream),
            name=tree.children[0].value,
            value=self._get_type(tree.children[1])
        )
        ad.define(self._module)
        # ad.emit(None, self._module, None, None, None)

    def const_def(self, tree):
        value = self._handle_expr(tree.children[1], {})
        cd = ast.Const(
            location=Location.FromTree(tree, self._stream),
            name=tree.children[0].value,
            value=value,
        )
        cd.define(self._module)
        # cd.emit(None, self._module, None, None, None)

    def c_array_type_def(self, tree):
        debug('defer', 'Making array')
        cad = ast.TypeDef(
            location=Location.FromTree(tree, self._stream),
            name=tree.children[0].value,
            type=ast.TypeSingletons.CARRAY.get_or_create_monomorphization(
                location=Location.FromTree(tree, self._stream),
                element_type=self._get_type(
                    tree.children[1].children[0], accept_missing=False
                ),
                element_count=int(tree.children[1].children[2])
            )
        )
        cad.define(self._module)
        # cad.emit(None, self._module, None, None, None)

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
                    type=self._get_type(param_type_obj),
                )
            )
        if return_type_obj is not None:
            return_type = self._get_type(return_type_obj.children[0])
        else:
            return_type = None

        cfd = ast.CFn(
            location=Location.FromTree(tree, self._stream),
            name=tree.children[0].value,
            type=ast.CFnType(
                location=Location.FromTree(tree, self._stream),
                parameters=parameters,
                return_type=return_type
            )
        )
        cfd.define(self._module)
        # cfd.emit(None, self._module, None, None, None)

    def c_struct_type_def(self, tree):
        debug('defer', 'Making struct')
        name = tree.children[0].value
        type = ast.CStructType(
            location=Location.FromTree(tree, self._stream),
            name=name,
            module=self._module
        )

        # [TODO] Check that this isn't already defined
        outer_types = {name: type}
        fields = []
        for i, field_obj in enumerate(tree.children[1:]):
            name_token, field_type_obj = field_obj.children
            fields.append(
                ast.Field(
                    location=Location.FromToken(name_token, self._stream),
                    name=name_token.value,
                    type=self._get_type(
                        field_type_obj, outer_types=outer_types
                    ),
                    index=i,
                )
            )

        type.set_fields(fields)

        csd = ast.CStructTypeDef(type)
        csd.define(self._module)
        # csd.emit(None, self._module, None, None, None)

    def c_union_type_def(self, tree):
        debug('defer', 'Making union')
        name = tree.children[0].value
        type = ast.CUnionType(
            location=Location.FromTree(tree, self._stream),
            name=tree.children[0].value,
            module=self._module
        )

        # [TODO] Check that this isn't already defined
        outer_types = {name: type}
        fields = []
        for i, field_obj in enumerate(tree.children[1:]):
            name_token, field_type_obj = field_obj.children
            fields.append(
                ast.Field(
                    location=Location.FromToken(name_token, self._stream),
                    name=name_token.value,
                    type=self._get_type(
                        field_type_obj, outer_types=outer_types
                    ),
                    index=i
                )
            )

        cud = ast.CUnionTypeDef(type)
        cud.define(self._module)
        # cud.emit(None, self._module, None, None, None)

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
                    type=self._get_type(param_type_obj),
                )
            )
        if return_type_obj is not None:
            return_type = self._get_type(return_type_obj.children[0])
        else:
            return_type = None

        scope = {param.name: param.type for param in parameters}

        code = self._process_code_block(code_block, scope=scope)

        # [TODO] Monomorphize here
        location = Location.FromTree(tree, self._stream)
        fd = ast.Fn(
            location=location,
            name=function_type_def.children[0].value,
            type=ast.FnType(
                location=location,
                monomorphizations=[
                    ast.MonoFnType(
                        location=location,
                        parameters=parameters,
                        return_type=return_type
                    )
                ]
            ),
            code=code
        )
        fd.define(self._module)
        # fd.emit(None, self._module, None, None, None)
