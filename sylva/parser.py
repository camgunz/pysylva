from collections import namedtuple

from . import ast
from . import debug
from . import errors
from . import token_type as TokenType
from . import types

from .lexer import Lexer
from .operator import Operator
from .token_category import TokenCategory


AttributeLookup = namedtuple(
    'AttributeLookup',
    ('location', 'attribute_name', 'enclosing_namespace'),
    defaults=(None,)
)

Scope = namedtuple(
    'Scope',
    ('vars',)
)


# pylint: disable=too-many-public-methods
class Parser:

    def __init__(self, module, data_source):
        self.module = module
        self.requirements = []
        self.aliases = {}
        self.implementations = []
        self.lexer = Lexer(data_source)

    # pylint: disable=redefined-outer-name
    def _expect(self, types=None, categories=None, token=None):
        debug(f'_expect({types}, {categories}, {token})')
        if token is None:
            token = self.lexer.lex()
        debug(f'{self.module.name}: {self.lexer.location} :: {token}')
        if not token.matches(token_types=types, token_categories=categories):
            if types and categories:
                raise errors.UnexpectedToken(token, types, categories)
            if types:
                raise errors.UnexpectedTokenType(token, types)
            if categories:
                raise errors.UnexpectedTokenCategory(token, categories)
            raise ValueError(
                'Neither types nor categories was given'
            )
        return token

    def _parse_literal_expr(self):
        # [TODO] Most (all?) of the time we want to also accept a constant
        #        expression, which is a little harder.
        token = self._expect(categories=[
            TokenCategory.Boolean,
            TokenCategory.Rune,
            TokenCategory.String,
            TokenCategory.Number
        ])

        if token.matches_type(TokenType.Boolean):
            return ast.BooleanLiteralExpr.from_token(token)
        if token.matches_type(TokenType.Rune):
            return ast.RuneLiteralExpr.from_token(token)
        if token.matches_type(TokenType.String):
            return ast.StringLiteralExpr.from_token(token)
        if token.matches_type(TokenType.Integer):
            return ast.IntegerLiteralExpr.from_token(token)
        if token.matches_type(TokenType.Float):
            return ast.FloatLiteralExpr.from_token(token)
        if token.matches_type(TokenType.Decimal):
            return ast.DecimalLiteralExpr.from_token(token)

    def _parse_list(self, opener, closer, parse_func, token=None):
        items = []
        self._expect(types=[opener], token=token)
        while True:
            token = self.lexer.lex()
            if token.matches_type(closer):
                break
            items.append(parse_func(token))
            token = self.lexer.lex()
            if token.matches_type(TokenType.Comma):
                continue
            if token.matches_type(closer):
                break
            raise errors.UnexpectedTokenType(token, [TokenType.Comma, closer])

        return items

    def _parse_type_parameter_list(self, token=None):
        return self._parse_list(
            TokenType.OpenParen,
            TokenType.CloseParen,
            lambda token: token.value,
            token=token
        )

    def _parse_field_list(self, parse_func, type_params=None, token=None):
        return dict(self._parse_list(
            TokenType.OpenBrace,
            TokenType.CloseBrace,
            lambda token: parse_func(type_params=type_params, token=token),
            token=token
        ))

    # pylint: disable=unused-argument
    def _parse_ctype_field(self, type_params=None, token=None):
        token = self._expect(types=[TokenType.Value], token=token)

        self._expect(types=[TokenType.Colon])
        field_type = self._parse_type(
            accept_default=False,
            deferred_lookups=type_params
        )
        return token.value, field_type

    def _parse_ctype_field_list(self, type_params=None, token=None):
        return self._parse_field_list(
            self._parse_ctype_field,
            type_params=type_params,
            token=token
        )

    def _parse_struct_field(self, type_params=None, token=None):
        token = self._expect(
            types=[TokenType.Value, TokenType.Variant],
            token=token
        )

        if token.matches_type(TokenType.Variant):
            return self.parse_variant_type(
                type_params=type_params,
                token=token
            )

        self._expect(types=[TokenType.Colon])
        field_type = self._parse_type(
            accept_default=False,
            deferred_lookups=type_params
        )
        return token.value, field_type

    def _parse_struct_field_list(self, type_params=None, token=None):
        return self._parse_field_list(
            self._parse_struct_field,
            type_params=type_params,
            token=token
        )

    def _parse_variant_field(self, type_params=None, token=None):
        token = self._expect(types=[TokenType.Value], token=token)
        self._expect(types=[TokenType.Colon])
        field_type = self._parse_type(
            accept_default=True,
            deferred_lookups=type_params
        )
        return token.value, field_type

    def _parse_variant_field_list(self, type_params=None, token=None):
        return self._parse_field_list(
            self._parse_variant_field,
            type_params=type_params,
            token=token
        )

    def _parse_function_signature(self, token=None):
        self._expect(types=[TokenType.OpenParen], token=token)
        parameters = []
        while True:
            token = self._expect(types=[TokenType.CloseParen, TokenType.Value])
            if token.matches_type(TokenType.CloseParen):
                break
            parameter_name = token.value
            self._expect(types=[TokenType.Colon])
            if self.lexer.next_matches(token_types=[TokenType.OpenBracket]):
                parameter_type = types.Array(*self._parse_array_type(
                    accept_default=False
                ))
            else:
                parameter_type = self._parse_type(accept_default=True)
            parameters.append((parameter_name, parameter_type))
            self.lexer.skip_next_if_matches(token_types=[TokenType.Comma])
        return_type = None
        if self.lexer.skip_next_if_matches([TokenType.Colon]):
            return_type = self._parse_type(accept_default=False)
        return parameters, return_type

    def _parse_cfn_or_cfntype(self, token_type, token=None):
        token = self._expect(types=[token_type], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        parameters, return_type = self._parse_function_signature()
        return location, name, parameters, return_type

    def _parse_array_type(self, accept_default, token=None):
        # strings: [str...]
        # strings: [str * 4]
        token = self._expect(types=[TokenType.OpenBracket], token=token)
        location = token.location.copy()
        self._expect(types=[TokenType.OpenBracket])
        element_type = self._parse_type(accept_default=accept_default)
        token = self._expect(types=[TokenType.Star, TokenType.Ellipsis])
        if token.matches_type(TokenType.Star):
            element_count = self._expect(
                categories=[TokenCategory.Integer]
            ).value
        elif token.matches_type(TokenType.Ellipsis):
            element_count = None
        return location, element_type, element_count

    def _parse_type(self, accept_default, deferred_lookups=None, token=None):
        # [TODO] Handle defaults (fn say(msg: str("hey")))

        token = token or self.lexer.lex()

        if token.matches_type(TokenType.Ampersand):
            return types.ReferencePointer(
                token.location.copy(),
                self.resolve_identifier(
                    *self.parse_identifier(),
                    deferred_lookups=deferred_lookups,
                ),
                self.lexer.skip_next_if_matches(token_types=[TokenType.Bang])
            )

        if token.matches_type(TokenType.Star):
            return types.OwnedPointer(
                token.location.copy(),
                self.resolve_identifier(
                    *self.parse_identifier(),
                    deferred_lookups=deferred_lookups,
                ),
            )

        return self.resolve_identifier(
            *self.parse_identifier(token=token),
            deferred_lookups=deferred_lookups,
        )

    def parse_identifier(self, token=None):
        token = self._expect(
            types=[
                TokenType.Value,
                TokenType.CFn,
                TokenType.CFnType,
                TokenType.CBlockFnType,
                TokenType.CStruct,
                TokenType.CUnion
            ],
            token=token
        )
        location = token.location.copy()
        namespaces = [token.value]
        while self.lexer.skip_next_if_matches([TokenType.Dot]):
            namespaces.append(self._expect(types=[TokenType.Value]).value)
        return location, '.'.join(namespaces)

    def parse_c_function_type(self, token=None):
        location, name, parameters, return_type = self._parse_cfn_or_cfntype(
            TokenType.CFnType,
            token=token
        )
        return types.CFunctionType(location, parameters, return_type, name)

    def parse_c_block_function_type(self, token=None):
        location, name, parameters, return_type = self._parse_cfn_or_cfntype(
            TokenType.CBlockFnType,
            token=token
        )
        return types.CBlockFunctionType(location, parameters, return_type, name)

    # pylint: disable=too-many-locals
    def resolve_identifier(self, location, identifier, deferred_lookups=None):
        namespaces = identifier.split('.')
        namespace = '.'.join(namespaces[:-1])
        base_identifier = namespaces[-1]

        if namespace:
            while namespace in self.aliases:
                namespace = self.aliases[namespace]

            if namespace not in self.requirements:
                raise errors.UndefinedSymbol(location, identifier)

            module = self.module.program.modules[namespace]
            value = module.lookup(base_identifier)
            if not value:
                raise errors.UndefinedSymbol(location, identifier)
            return value

        if identifier in self.aliases:
            while identifier in self.aliases:
                identifier = self.aliases[identifier]
            return identifier

        if deferred_lookups and identifier in deferred_lookups:
            return ast.DeferredLookup(location, identifier)

        if identifier in types.BUILTINS:
            sylva_type = types.BUILTINS[identifier]
            if isinstance(sylva_type, types.SylvaMetaType):
                return sylva_type.parse(None, self)
            return sylva_type

        if identifier == 'carray':
            self._expect(types=[TokenType.OpenParen])

            element_type = self.resolve_identifier(
                *self.parse_identifier(),
                deferred_lookups=deferred_lookups
            )

            element_count = None
            if self.lexer.skip_next_if_matches(token_types=[TokenType.Comma]):
                element_count = self._parse_literal_expr()
                if not isinstance(element_count, ast.NumericLiteralExpr):
                    raise errors.InvalidExpressionType(
                        location,
                        'NumericLiteralExpr',
                        type(element_count).__name__
                    )

            self._expect(types=[TokenType.CloseParen])
            return types.CArray(location.copy(), element_type, element_count)

        if identifier == 'cbitfield':
            self._expect(types=[TokenType.OpenParen])

            field_type = self.resolve_identifier(
                *self.parse_identifier(),
                deferred_lookups=deferred_lookups
            )

            self._expect(types=[TokenType.Comma])

            field_size = self._parse_literal_expr()
            if not isinstance(field_size, ast.NumericLiteralExpr):
                raise errors.InvalidExpressionType(
                    location,
                    'NumericLiteralExpr',
                    type(field_size).__name__
                )

            self._expect(types=[TokenType.CloseParen])
            return types.CBitField(location.copy(), field_type, field_size)

        if identifier == 'cfntype':
            return types.CFunctionType(
                location.copy(),
                *self._parse_function_signature()
            )

        if identifier == 'cblockfntype':
            return types.CBlockFunctionType(
                location.copy(),
                *self._parse_function_signature()
            )

        if identifier == 'cptr':
            self._expect(types=[TokenType.OpenParen])
            ref_type = self.resolve_identifier(
                *self.parse_identifier(),
                deferred_lookups=deferred_lookups
            )

            ref_type_is_mutable = self.lexer.skip_next_if_matches(
                token_types=[TokenType.Bang]
            )

            self._expect(types=[TokenType.CloseParen])
            return types.CPtr(
                location.copy(),
                ref_type,
                ref_type_is_mutable,
                self.lexer.skip_next_if_matches(token_types=[TokenType.Bang])
            )

        if identifier == 'cstruct':
            return types.CStruct(location, self._parse_ctype_field_list())

        if identifier == 'cunion':
            return types.CUnion(location, self._parse_ctype_field_list())

        value = self.module.lookup(identifier)
        if value:
            return value

        raise errors.UndefinedSymbol(location, identifier)

    def parse_code(self, token=None):
        # self.scopes.appendLeft({})
        code = []
        self._expect(types=[TokenType.OpenBrace])
        token = self.lexer.get_next_if_not_matches([TokenType.CloseBrace])
        while token:
            debug(f'Got code token {token}')
            code.append(self.parse_code_node(token))
            token = self.lexer.get_next_if_not_matches([TokenType.CloseBrace])
        self._expect(types=[TokenType.CloseBrace])
        # self.scopes.popLeft()
        return code

    def parse_module(self, token=None):
        # mod math
        self._expect(types=[TokenType.Module], token=token)
        _, mod_name = self.parse_identifier()
        if mod_name != self.module.name:
            raise RuntimeError(
                f'Expected module {self.module.name}; got {mod_name}'
            )
        return mod_name

    def parse_requirement(self, token=None):
        # req math
        self._expect(types=[TokenType.Requirement], token=token)
        _, req = self.parse_identifier()
        if req not in self.module.dependency_names:
            raise RuntimeError(f'Requirement {req} not found in dependencies')
        return req

    def parse_alias(self, token=None):
        # alias short_and_sweet: long_and_salllllllllty_it_sure_is_yeah
        self._expect(types=[TokenType.Alias], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        self._expect(types=[TokenType.Colon])
        target_location, target_identifier = self.parse_identifier()
        if name == target_identifier:
            raise errors.RedundantAlias(location, name)
        if name in self.aliases:
            raise errors.DuplicateAlias(location, name)
        target = self.resolve_identifier(target_location, target_identifier)
        return name, target

    def parse_const(self, token=None):
        # const MAX_SIZE: 64u
        token = self._expect([TokenType.Const], token=token)
        name_token = self._expect([TokenType.Value])
        self._expect([TokenType.Colon])
        literal_expr = self._parse_literal_expr()
        return name_token.value, literal_expr

    def parse_enum_type(self, token=None):
        raise NotImplementedError()

    def parse_function_type(self, token=None):
        token = self._expect(types=[TokenType.FnType], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        parameters, return_type = self._parse_function_signature()
        return types.FunctionType(location, parameters, return_type, name)

    def parse_function(self, token=None):
        token = self._expect(types=[TokenType.Fn], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        parameters, return_type = self._parse_function_signature()
        code = self.parse_code()
        return types.Function(location, parameters, return_type, code, name)

    def parse_c_function(self, token=None):
        location, name, parameters, return_type = self._parse_cfn_or_cfntype(
            TokenType.CFn,
            token=token
        )
        return types.CFunction(location, parameters, return_type, name)

    def parse_range_type(self, token=None):
        raise NotImplementedError()

    def parse_c_struct_type(self, token=None):
        token = self._expect(types=[TokenType.CStruct], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        fields = self._parse_ctype_field_list(type_params=[name])
        return types.CStruct(location, fields, name=name)

    def parse_c_union_type(self, token=None):
        token = self._expect(types=[TokenType.CUnion], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        fields = self._parse_ctype_field_list(type_params=[name])
        return types.CUnion(location, fields, name=name)

    def parse_struct_type(self, token=None):
        token = self._expect(types=[TokenType.Struct], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        type_params = []
        paren_token = self.lexer.get_next_if_matches([TokenType.OpenParen])
        if paren_token:
            type_params = self._parse_type_parameter_list(token=paren_token)
        fields = self._parse_struct_field_list(type_params=type_params)
        return types.Struct(location, name, type_params, fields)

    def parse_variant_type(self, type_params=None, token=None):
        token = self._expect(types=[TokenType.Variant], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        fields = self._parse_variant_field_list(type_params=type_params)
        self.module.define(name, types.Variant(location, name, fields))

    def parse_interface_type(self, token=None):
        raise NotImplementedError()

    def parse_implementation(self, token=None):
        token = self._expect(types=[TokenType.Implementation], token=token)
        location = token.location.copy()
        interface_location, interface_identifier = self.parse_identifier()
        interface = self.resolve_identifier(
            interface_location,
            interface_identifier
        )
        self._expect(types=[TokenType.Comma])
        impl_type_location, impl_type_identifier = self.parse_identifier()
        implementing_type = self.resolve_identifier(
            impl_type_location,
            impl_type_identifier
        )
        self._expect(types=[TokenType.OpenBrace])
        funcs = []
        while not self.lexer.next_matches(token_types=[TokenType.CloseBrace]):
            funcs.append(self.parse_function())
        return ast.Implementation(location, interface, implementing_type, funcs)

    def parse_var(self, token=None):
        raise NotImplementedError()

    def parse_if(self, token=None):
        token = self._expect(types=[TokenType.If], token=token)
        location = token.location.copy()
        self._expect(types=[TokenType.OpenParen])
        conditional_expr = self.parse_expression()
        self._expect(types=[TokenType.CloseParen])
        code = self.parse_code()
        return ast.If(location, conditional_expr, code)

    def parse_else(self, token=None):
        token = self._expect(types=[TokenType.Else], token=token)
        location = token.location.copy()
        if self.lexer.next_matches(token_types=[TokenType.If]):
            return ast.Else(location, self.parse_if())
        return ast.Else(location, self.parse_code())

    def parse_switch(self, token=None):
        raise NotImplementedError()

    def parse_match(self, token=None):
        raise NotImplementedError()

    def parse_case(self, token=None):
        raise NotImplementedError()

    def parse_default(self, token=None):
        raise NotImplementedError()

    def parse_for(self, token=None):
        raise NotImplementedError()

    def parse_loop(self, token=None):
        token = self._expect(types=[TokenType.Loop], token=token)
        return ast.Loop(token.location.copy(), self.parse_code())

    def parse_while(self, token=None):
        token = self._expect(types=[TokenType.While], token=token)
        location = token.location.copy()
        self._expect(types=[TokenType.OpenParen])
        conditional_expr = self.parse_expression()
        self._expect(types=[TokenType.CloseParen])
        code = self.parse_code()
        return ast.While(location, conditional_expr, code)

    def parse_break(self, token=None):
        token = self._expect(types=[TokenType.Break], token=token)
        return ast.Break(token.location.copy())

    def parse_continue(self, token=None):
        token = self._expect(types=[TokenType.Continue], token=token)
        return ast.Continue(token.location.copy())

    def parse_return(self, token=None):
        token = self._expect(types=[TokenType.Return], token=token)
        location = token.location.copy()
        return ast.Return(location, self.parse_expression())

    def parse_expression(self, prec=0, token=None):
        # [TODO] I don't really get how expressions terminate

        token = token or self.lexer.lex()
        expr = None

        if token.matches_type(TokenType.Integer):
            expr = ast.IntegerLiteralExpr.from_token(token)
        elif token.matches_type(TokenType.Float):
            expr = ast.FloatLiteralExpr.from_token(token)
        elif token.matches_type(TokenType.Decimal):
            expr = ast.DecimalLiteralExpr.from_token(token)
        elif token.matches_type(TokenType.Boolean):
            expr = ast.BooleanLiteralExpr.from_token(token)
        elif token.matches_type(TokenType.Rune):
            expr = ast.RuneLiteralExpr.from_token(token)
        elif token.matches_type(TokenType.String):
            expr = ast.StringLiteralExpr.from_token(token)
        elif token.matches_type(TokenType.Plus):
            expr = ast.UnaryExpr(
                token.location.copy(),
                Operator.Plus,
                self.parse_expression(prec=Operator.max_precedence()+1)
            )
        elif token.matches_type(TokenType.Minus):
            expr = ast.UnaryExpr(
                token.location.copy(),
                Operator.Minus,
                self.parse_expression(prec=Operator.max_precedence()+1)
            )
        elif token.matches_type(TokenType.Tilde):
            expr = ast.UnaryExpr(
                token.location.copy(),
                Operator.BinaryNot,
                self.parse_expression(prec=Operator.max_precedence()+1)
            )
        elif token.matches_type(TokenType.Bang):
            expr = ast.UnaryExpr(
                token.location.copy(),
                Operator.Not,
                self.parse_expression(prec=Operator.max_precedence()+1)
            )
        elif token.matches_category(TokenType.Value):
            identifier = self.parse_identifier(token)
            lookup_expr = ast.LookupExpr(token.location.copy(), identifier)
            if self.lexer.next_matches(token_types=[TokenType.OpenParen]):
                expr = ast.CallExpr(
                    token.location.copy(),
                    lookup_expr,
                    self._parse_list(
                        opener=TokenType.OpenParen,
                        closer=TokenType.CloseParen,
                        parse_func=self.parse_expression
                    )
                )
            elif self.lexer.skip_next_if_matches(
                    token_types=[TokenType.OpenBracket]):
                index_value_expr = self.parse_expression()
                self._expect(types=[TokenType.CloseBracket])
                expr = ast.IndexExpr(
                    token.location.copy(),
                    lookup_expr,
                    index_value_expr
                )
            else:
                expr = lookup_expr
        else:
            # [NOTE] Here is potentially where we can look for a "this is not
            #        an expression" token, i.e. a semicolon, a line break, etc.
            raise errors.InvalidExpression(token.location)

        next_token = self.lexer.get_next_if_matches(
            token_categories=[TokenCategory.Operator]
        )

        if not next_token:
            return expr

        op = next_token.token_type.operator
        while prec < op.precedence:
            expr = ast.BinaryExpr(
                token.location.copy(),
                expr,
                op,
                self.parse_expression(op.precedence)
            )

        return expr

    def parse_code_node(self, token=None):
        token = token or self.lexer.lex()
        if token.matches_type(TokenType.Var):
            return self.parse_var(token)
        if token.matches_type(TokenType.If):
            return self.parse_if(token)
        if token.matches_type(TokenType.Else):
            return self.parse_else(token)
        if token.matches_type(TokenType.Switch):
            return self.parse_switch(token)
        if token.matches_type(TokenType.Match):
            return self.parse_switch(token)
        if token.matches_type(TokenType.Case):
            return self.parse_case(token)
        if token.matches_type(TokenType.Default):
            return self.parse_default(token)
        if token.matches_type(TokenType.For):
            return self.parse_for(token)
        if token.matches_type(TokenType.Loop):
            return self.parse_loop(token)
        if token.matches_type(TokenType.While):
            return self.parse_while(token)
        if token.matches_type(TokenType.Break):
            return self.parse_break(token)
        if token.matches_type(TokenType.Continue):
            return self.parse_continue(token)
        if token.matches_type(TokenType.Return):
            return self.parse_return(token)
        return self.parse_expression(token)

    def parse(self):  # pylint: disable=too-many-locals
        while True:
            try:
                token = self._expect(types=[
                    TokenType.Alias,
                    TokenType.Const,
                    TokenType.Enum,
                    TokenType.FnType,
                    TokenType.CFnType,
                    TokenType.CBlockFnType,
                    TokenType.Fn,
                    TokenType.CFn,
                    TokenType.Interface,
                    TokenType.Implementation,
                    TokenType.Module,
                    TokenType.Range,
                    TokenType.Requirement,
                    TokenType.Struct,
                    TokenType.CStruct,
                    TokenType.CUnion,
                ])
            except errors.EOF:
                break
            # print(self.lexer, token)
            if token.matches_type(TokenType.Alias):
                name, target = self.parse_alias(token)
                self.aliases[name] = target
                print(f'<Alias {name} -> {target}>')
            elif token.matches_type(TokenType.Const):
                name, literal_expr = self.parse_const(token)
                self.module.define(name, literal_expr)
                print(f'<Const {name} -> {literal_expr}>')
            elif token.matches_type(TokenType.Enum):
                enum = self.parse_enum_type(token)
                self.module.define(enum.name, enum)
                print(enum)
            elif token.matches_type(TokenType.FnType):
                func_type = self.parse_function_type(token)
                self.module.define(func_type.name, func_type)
                print(func_type)
            elif token.matches_type(TokenType.CFnType):
                cfunc_type = self.parse_c_function_type(token)
                self.module.define(cfunc_type.name, cfunc_type)
                print(cfunc_type)
            elif token.matches_type(TokenType.CBlockFnType):
                cblockfunc_type = self.parse_c_block_function_type(token)
                self.module.define(cblockfunc_type.name, cblockfunc_type)
                print(cblockfunc_type)
            elif token.matches_type(TokenType.Fn):
                func = self.parse_function(token)
                self.module.define(func.name, func)
                print(func)
            elif token.matches_type(TokenType.CFn):
                cfunc = self.parse_c_function(token)
                self.module.define(cfunc.name, cfunc)
                print(cfunc)
            elif token.matches_type(TokenType.Interface):
                interface = self.parse_interface_type(token)
                self.module.define(interface.name, interface)
                print(interface)
            elif token.matches_type(TokenType.Implementation):
                implementation = self.parse_implementation(token)
                # [TODO] Mark type as having implemented the interface
                # [TODO] Mark interface as having type as an implementation
                self.module.implementations.append(implementation)
                print(implementation)
            elif token.matches_type(TokenType.Module):
                mod = self.parse_module(token)
                print(f'<Module {mod}>')
            elif token.matches_type(TokenType.Range):
                range_ = self.parse_range_type(token)
                self.module.define(range_.name, range_)
                print(range_)
            elif token.matches_type(TokenType.Requirement):
                requirement = self.parse_requirement(token)
                self.requirements.append(requirement)
                print(f'<Requirement {requirement}>')
            elif token.matches_type(TokenType.Struct):
                struct = self.parse_struct_type(token)
                self.module.define(struct.name, struct)
                print(struct)
            elif token.matches_type(TokenType.CStruct):
                cstruct = self.parse_c_struct_type(token)
                self.module.define(cstruct.name, cstruct)
                print(cstruct)
            elif token.matches_type(TokenType.CUnion):
                cunion = self.parse_c_union_type(token)
                self.module.define(cunion.name, cunion)
                from pprint import pprint
                pprint(cunion)
