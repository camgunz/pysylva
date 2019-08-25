from collections import deque, namedtuple

import functools

from . import ast
from . import errors
from . import operator
from . import types
from .lexer import Lexer
from .token import TokenCategory, TokenType


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
        self.lexer = Lexer(data_source)

    # pylint: disable=redefined-outer-name
    def _expect(self, types=None, categories=None, token=None):
        token = token or self.lexer.lex()
        print(f'{self.module.name}: {self.lexer.location} :: {token}')
        if not token.matches(types, categories):
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

    def _parse_flat_identifier(self, token=None):
        token = self._expect(types=[TokenType.Value], token=token)
        location = token.location.copy()
        namespaces = [token.value]
        while True:
            dot = self.lexer.get_next_if_matches([TokenType.AttributeLookup])
            if not dot:
                break
            namespaces.append(self._expect(types=[TokenType.Value]).value)
        return location, '.'.join(namespaces)

    def _resolve_identifier(self, token=None):
        location, identifier = self._parse_flat_identifier(token)

        namespace = identifier.split('.')
        name = namespace.pop()
        namespace = '.'.join(namespace)

        if namespace:
            while namespace in self.aliases:
                namespace = self.aliases[namespace]

            if namespace not in self.requirements:
                raise errors.UndefinedSymbol(location, identifier)

            module = self.module.program.modules[namespace]
        else:
            module = self.module

        value = module.lookup(name)
        if not value:
            raise errors.UndefinedSymbol(location, identifier)
        return value

    def _parse_code(self, token=None):
        # self.scopes.appendLeft({})
        code = []
        self._expect(types=[TokenType.OpenBrace])
        token = self.lexer.get_next_if_not_matches([TokenType.CloseBrace])
        while token:
            print(f'Got code token {token}')
            code.append(self.parse_code_node(token))
            token = self.lexer.get_next_if_not_matches([TokenType.CloseBrace])
        self._expect(types=[TokenType.CloseBrace])
        # self.scopes.popLeft()
        return code

    def _parse_function_signature(self, token=None):
        self._expect(types=[TokenType.OpenParen], token=token)
        parameters = []
        while True:
            token = self._expect(types=[TokenType.CloseParen, TokenType.Value])
            if token.token_type == TokenType.CloseParen:
                break
            parameter_name = token.value
            self._expect(types=[TokenType.Colon])
            # [TODO] Default params
            parameter_value = self._resolve_identifier()
            parameters.append((parameter_name, parameter_value))
            self.lexer.skip_next_if_matches(token_types=[TokenType.Comma])
        return_type = None
        state = self.lexer.get_state()
        token = self.lexer.lex()
        if token.token_type == TokenType.Colon:
            return_type = self._resolve_identifier()
        else:
            self.lexer.set_state(state)
        return parameters, return_type

    def parse(self):
        while True:
            try:
                token = self._expect(types=[
                    TokenType.Requirement,
                    TokenType.Alias,
                    TokenType.Module,
                    TokenType.Fn,
                    TokenType.FnType,
                    TokenType.Struct,
                    TokenType.Array,
                    TokenType.Implementation,
                ])
            except errors.EOF:
                break
            if token.token_type == TokenType.Requirement:
                self.parse_requirement(token)
            elif token.token_type == TokenType.Alias:
                self.parse_alias(token)
            elif token.token_type == TokenType.Module:
                self._parse_flat_identifier()
                continue
            elif token.token_type == TokenType.Fn:
                self.parse_function(token)
            elif token.token_type == TokenType.FnType:
                self.parse_function_type(token)
            elif token.token_type == TokenType.Struct:
                self.parse_struct_type(token)
            elif token.token_type == TokenType.Array:
                self.parse_array_type(token)
            elif token.token_type == TokenType.Implementation:
                self.parse_implementation(token)

    def parse_requirement(self, token=None):
        self._expect(types=[TokenType.Requirement], token=token)
        location, requirement = self._parse_flat_identifier()
        if requirement not in self.module.dependency_names:
            raise RuntimeError('Requirement not found in dependencies')
        self.requirements.append(requirement)

    def parse_alias(self, token=None):
        self._expect(types=[TokenType.Alias], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        self._expect(types=[TokenType.Colon])
        alias_location, alias = self._parse_flat_identifier()
        if name == alias:
            raise errors.RedundantAlias(location, name)
        if name in self.aliases:
            raise errors.DuplicateAlias(location, name)
        self.aliases[name] = alias

    def parse_struct_type(self, token=None):
        token = self._expect(types=[TokenType.Struct], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        self._expect(types=[TokenType.OpenBrace])
        token = self.lexer.get_next_if_not_matches([TokenType.CloseBrace])
        fields = []
        while token:
            field_name = self._expect(types=[TokenType.Value])
            self._expect(types=[TokenType.Colon])
            field_type = self._resolve_identifier()
            fields.append((field_name, field_type))
            self.lexer.skip_next_if_matches(token_types=[TokenType.Comma])
            token = self.lexer.get_next_if_not_matches([TokenType.CloseBrace])
        self.module.define(name, types.Struct(location, name, fields))

    def parse_array_type(self, token=None):
        token = self._expect(types=[TokenType.Array], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        self._expect(types=[TokenType.OpenBracket])
        element_type = self._resolve_identifier()
        if self.lexer.skip_next_if_matches(token_types=[TokenType.Multiply]):
            element_count = self._expect(
                categories=[TokenCategory.Integer]
            ).value
        else:
            element_count = None
        self.module.define(
            name,
            types.Array(location, name, element_type, element_count)
        )

    def parse_function_type(self, token=None):
        token = self._expect(types=[TokenType.FnType], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        parameters, return_type = self._parse_function_signature()
        return types.FunctionType(location, name, parameters, return_type)

    def parse_function(self, token=None):
        token = self._expect(types=[TokenType.Fn], token=token)
        location = token.location.copy()
        name = self._expect(types=[TokenType.Value]).value
        parameters, return_type = self._parse_function_signature()
        code = self._parse_code()
        return types.Function(location, name, parameters, return_type, code)

    def parse_implementation(self, token=None):
        raise NotImplementedError()

    def parse_val(self, token=None):
        raise NotImplementedError()

    def parse_var(self, token=None):
        raise NotImplementedError()

    def parse_if(self, token=None):
        raise NotImplementedError()

    def parse_else(self, token=None):
        raise NotImplementedError()

    def parse_switch(self, token=None):
        raise NotImplementedError()

    def parse_case(self, token=None):
        raise NotImplementedError()

    def parse_default(self, token=None):
        raise NotImplementedError()

    def parse_do(self, token=None):
        raise NotImplementedError()

    def parse_for(self, token=None):
        raise NotImplementedError()

    def parse_loop(self, token=None):
        raise NotImplementedError()

    def parse_while(self, token=None):
        raise NotImplementedError()

    def parse_break(self, token=None):
        raise NotImplementedError()

    def parse_continue(self, token=None):
        raise NotImplementedError()

    def parse_error(self, token=None):
        raise NotImplementedError()

    def parse_fallthrough(self, token=None):
        raise NotImplementedError()

    def parse_return(self, token=None):
        raise NotImplementedError()

    def parse_with(self, token=None):
        raise NotImplementedError()

    def parse_call_expression(self, token=None):
        # identifier open_paren expr close_paren
        token = token or self.lexer.lex()
        location = token.location.copy()
        function = self._resolve_identifier(token)
        self._expect(types=[TokenType.OpenParen])
        arguments = []
        while True:
            token = self.lexer.get_next_if_not_matches([TokenType.CloseParen])
            if not token:
                break
            arguments.append(self.parse_expression(token))
            self.lexer.skip_next_if_matches(token_types=[TokenType.Comma])
        self._expect(types=[TokenType.CloseParen])
        return ast.CallExpr(location, function, arguments)

    def parse_unary_expression(self, token=None):
        token = self._expect(categories=[TokenCategory.Operator], token=token)
        if not token.token_type.unary:
            raise errors.InvalidExpression(token.location)
        location = token.location.copy()
        return ast.UnaryExpr(
            location,
            operator.Operator.FromToken(token, arity=operator.Arity.Unary),
            self.parse_expression()
        )

    def _parse_binary_expression(self, lhs, token=None):
        token = self._expect(categories=[TokenCategory.Operator], token=token)
        if not token.token_type.binary:
            raise errors.InvalidExpression(token.location)
        location = token.location.copy()
        return ast.BinaryExpr(
            location,
            operator.Operator.FromToken(token, arity=operator.Arity.Binary),
            lhs,
            self.parse_expression()
        )

    def parse_expression(self, token=None):
        # [TODO] Part of the grammar is that expressions do not span lines
        #        unless surrounded by parentheses.
        token = token or self.lexer.lex()
        expr = None
        if TokenCategory.Operator in token.categories:
            expr = self.parse_unary_expression(token)
        elif token.token_type == TokenType.Boolean:
            expr = ast.BooleanExpr(
                token.location.copy(),
                token.value == 'true'
            )
        elif token.token_type == TokenType.Rune:
            expr = ast.RuneExpr(token.location.copy(), token.value)
        elif token.token_type == TokenType.String:
            expr = ast.StringExpr(token.location.copy(), token.value)
        elif token.token_type == TokenType.Decimal:
            expr = ast.DecimalExpr(token.location.copy(), token.value)
        elif token.token_type == TokenType.Float:
            expr = ast.FloatExpr(token.location.copy(), token.value)
        elif TokenCategory.Integer in token.categories:
            expr = ast.IntegerExpr(
                token.location.copy(),
                token.value,
                signed=token.signed,
                base=token.base
            )
        else:
            state = self.lexer.get_state()
            expr = self._resolve_identifier(token)
            if self.lexer.next_matches([TokenType.OpenParen]):
                self.lexer.set_state(state)
                expr = self.parse_call_expression(token)
        if not expr:
            raise errors.InvalidExpression(token.location)
        binary_operator = self.lexer.get_next_if_matches(token_categories=[
            TokenCategory.Operator
        ])
        if binary_operator:
            expr = self._parse_binary_expression(expr, binary_operator)
        return expr

    def parse_code_node(self, token=None):
        token = token or self.lexer.lex()
        if token.token_type == TokenType.Val:
            return self.parse_val(token)
        if token.token_type == TokenType.Var:
            return self.parse_var(token)
        if token.token_type == TokenType.If:
            return self.parse_if(token)
        if token.token_type == TokenType.Else:
            return self.parse_else(token)
        if token.token_type == TokenType.Switch:
            return self.parse_switch(token)
        if token.token_type == TokenType.Case:
            return self.parse_case(token)
        if token.token_type == TokenType.Default:
            return self.parse_default(token)
        if token.token_type == TokenType.Do:
            return self.parse_do(token)
        if token.token_type == TokenType.For:
            return self.parse_for(token)
        if token.token_type == TokenType.Loop:
            return self.parse_loop(token)
        if token.token_type == TokenType.While:
            return self.parse_while(token)
        if token.token_type == TokenType.Break:
            return self.parse_break(token)
        if token.token_type == TokenType.Continue:
            return self.parse_continue(token)
        if token.token_type == TokenType.Error:
            return self.parse_error(token)
        if token.token_type == TokenType.Fallthrough:
            return self.parse_fallthrough(token)
        if token.token_type == TokenType.Return:
            return self.parse_return(token)
        if token.token_type == TokenType.With:
            return self.parse_with(token)
        return self.parse_expression(token)
