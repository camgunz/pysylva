import lark

from sylva import debug, errors
from sylva.builtins import (
    CPTR,
    CVOID,
    CVOIDEX,
    IntValue,
    STR,
    StrValue,
    TypeModifier,
    get_int_type,
)
from sylva.code_block import CodeBlock
from sylva.expr import (
    AttributeLookupExpr,
    CallExpr,
    CPtrExpr,
    CVoidExpr,
    LookupExpr,
    UnaryExpr,
    VariantFieldTypeLookupExpr,
)
from sylva.location import Location
from sylva.operator import Operator
from sylva.stmt import DefaultBlock, MatchBlock, MatchCaseBlock, ReturnStmt


class RuntimeASTBuilder(lark.visitors.Transformer_InPlaceRecursive):

    def __init__(self, program, module, location=None):
        super().__init__()
        self._program = program
        self._module = module
        self._stream = location.stream if location else None

    def expr(self, parts):
        debug('ast_builder', f'expr: {parts}')
        mod, expr = TypeModifier.separate_type_mod(parts)
        expr.type.mod = mod

        return expr

    def c_pointer_expr(self, parts):
        debug('ast_builder', f'c_pointer_expr: {parts}')
        cptr = parts.pop(0)
        expr = parts.pop(0)
        is_exclusive = bool(parts)
        location = Location.FromToken(cptr, stream=self._stream)

        return CPtrExpr(
            location=location,
            type=CPTR.build_type(
                location=location,
                mod=TypeModifier.CMut if is_exclusive else TypeModifier.NoMod,
                referenced_type=expr.type,
            ),
            expr=expr,
        )

    def c_void_expr(self, parts):
        debug('ast_builder', f'c_void_expr: {parts}')
        cvoid = parts.pop(0)
        expr = parts.pop(0)
        is_exclusive = bool(parts)
        location = Location.FromToken(cvoid, stream=self._stream)

        return CVoidExpr(
            location=location,
            type=CVOIDEX if is_exclusive else CVOID,
            expr=expr,
        )

    def call_expr(self, parts):
        debug('ast_builder', f'call_expr: {parts}')
        # [TODO] After looking up the function, we need to get the right
        #        monomorphization.
        func_lookup, args = parts[0], parts[1:]
        return CallExpr(
            location=func_lookup.location.copy(),
            function=func_lookup,
            arguments=args,
            type=None
        )

    def code_block(self, parts):
        debug('ast_builder', f'code_block: {parts}')
        return CodeBlock(code=parts)

    def default_block(self, parts):
        debug('ast_builder', f'match_case_block: {parts}')
        return DefaultBlock(
            location=Location.FromToken(parts[0], stream=self._stream),
            code=parts[1]
        )

    def int_expr(self, parts):
        debug('ast_builder', f'int_expr: {parts}')
        int_token = parts[0].children[0]

        return IntValue.FromString(
            location=Location.FromToken(int_token, stream=self._stream),
            strval=int_token.value
        )

    def match_block(self, parts):
        debug('ast_builder', f'match_block: {parts}')
        return MatchBlock(
            location=Location.FromToken(parts.pop(0), stream=self._stream),
            variant_expr=parts.pop(0),
            default_case=( # yapf: ignore
                parts.pop(-1)
                if parts and isinstance(parts[-1], DefaultBlock)
                else None
            ),
            match_cases=parts,
        )

    def match_case_block(self, parts):
        debug('ast_builder', f'match_case_block: {parts}')
        case, var_name, var_type, code_block = parts
        return MatchCaseBlock(
            location=Location.FromToken(case, stream=self._stream),
            variant_name=var_name.value,
            variant_field_type_lookup_expr=VariantFieldTypeLookupExpr(
                location=Location.FromToken(var_type, stream=self._stream),
                name=var_type.value
            ),
            code=code_block,
        )

    def return_stmt(self, parts):
        debug('ast_builder', f'match_case_block: {parts}')
        return ReturnStmt(
            location=Location.FromToken(parts[0], stream=self._stream),
            expr=parts[1]
        )

    def runtime_lookup_expr(self, parts):
        debug('ast_builder', f'runtime_lookup_expr: {parts}')
        name = parts.pop(0)

        expr = LookupExpr(
            location=Location.FromToken(name, stream=self._stream),
            name=name.value,
            type=None
        )

        while parts:
            reflection = parts.pop(0).value == '::'
            attr_name = parts.pop(0)

            expr = AttributeLookupExpr(
                location=Location.FromToken(attr_name, stream=self._stream),
                name=attr_name.value,
                obj=expr,
                reflection=reflection,
                type=None
            )

        return expr

    def string_expr(self, parts):
        debug('ast_builder', f'string_expr: {parts}')
        str_token = parts[0].children[0]
        location = Location.FromToken(str_token, stream=self._stream)

        return StrValue(
            location=Location.FromToken(str_token, stream=self._stream),
            value=str_token.value[1:-1],
            type=STR.build_type(
                location=location,
                element_count=IntValue(
                    type=get_int_type(bits=None, signed=False),
                    value=len(str_token.value) - 2
                )
            )
        )

    def unary_expr(self, parts):
        debug('ast_builder', f'unary_expr: {parts}')
        op, expr = parts
        location = Location.FromToken(op, stream=self._stream),
        operator = Operator.lookup(op.value, 1)
        if operator is None:
            raise errors.NoSuchUnaryOperator(location, op.value)

        return UnaryExpr(
            location=location, operator=operator, expr=expr, type=expr.type
        )
