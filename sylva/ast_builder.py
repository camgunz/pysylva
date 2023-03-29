from dataclasses import dataclass

import lark

from sylva import debug, errors
from sylva.builtins import (  # noqa: F401
    ARRAY,
    ArrayValue,
    BOOL,
    BoolValue,
    C128,
    C16,
    C32,
    C64,
    CARRAY,
    CArrayValue,
    CBITFIELD,
    CBLOCKFN,
    CBitFieldValue,
    CFN,
    CFnValue,
    CodeBlock,
    CPTR,
    CPtrValue,
    CSTR,
    CSTRUCT,
    CStrValue,
    CStructValue,
    CUNION,
    CUnionValue,
    CVOID,
    CVOIDEX,
    CVoidValue,
    ComplexType,
    ComplexValue,
    DYNARRAY,
    DynarrayValue,
    ENUM,
    EnumValue,
    F128,
    F16,
    F32,
    F64,
    FN,
    FloatType,
    FloatValue,
    FnValue,
    I128,
    I16,
    I32,
    I64,
    I8,
    IntType,
    IntValue,
    RANGE,
    RUNE,
    RangeValue,
    RuneValue,
    STR,
    STRING,
    STRUCT,
    SelfReferentialField,
    StrValue,
    StringValue,
    StructValue,
    SylvaDef,
    SylvaField,
    SylvaObject,
    SylvaType,
    SylvaValue,
    TypeDef,
    TypeModifier,
    TypePlaceholder,
    U128,
    U16,
    U32,
    U64,
    U8,
    VARIANT,
    VariantValue,
)
from sylva.expr import (
    AttributeLookupExpr,
    CallExpr,
    CPtrExpr,
    CVoidExpr,
    IntLiteralExpr,
    LookupExpr,
    StrLiteralExpr,
    UnaryExpr,
    VariantFieldTypeLookupExpr,
)
from sylva.location import Location
from sylva.operator import Operator
from sylva.stmt import DefaultBlock, MatchBlock, MatchCaseBlock, ReturnStmt


@dataclass(kw_only=True)
class UndefinedSymbol:
    location: Location
    name: str
    type: SylvaType | None


class ASTBuilder(lark.visitors.Transformer_InPlaceRecursive):

    def __init__(self, program, module, location=None):
        super().__init__()
        self._program = program
        self._module = module
        self._stream = location.stream if location else None

    def c_array_type_def(self, parts):
        debug('ast_builder', f'c_array_type_def: {parts}')
        carray = parts.pop(0)
        name = parts.pop(0).value
        array_type_expr = parts.pop(0)
        type_expr, count_expr = array_type_expr.children
        location = Location.FromToken(carray, stream=self._stream)

        typedef = TypeDef(
            location=location,
            name=name,
            type=CARRAY.build_type(
                location=location,
                element_type=type_expr.eval(self._module),
                element_count=count_expr.eval(self._module),
            )
        )

        self._module.add_def(typedef)

        return typedef

    def c_array_type_literal_expr(self, parts):
        debug('ast_builder', f'c_array_type_literal_expr: {parts}')
        mod, parts = TypeModifier.separate_type_mod(parts)
        carray, element_type, element_count = parts
        location = Location.FromToken(carray, stream=self._stream)

        return CARRAY.build_type(
            location=location,
            mod=mod,
            element_type=element_type,
            element_count=element_count,
        )

    def c_bit_field_type_literal_expr(self, parts):
        debug('ast_builder', f'c_bit_field_type_literal_expr: {parts}')
        mod, parts = TypeModifier.separate_type_mod(parts)
        cbitfield, int_type_expr, field_size = parts
        location = Location.FromToken(cbitfield, stream=self._stream)
        int_type = LookupExpr(
            location=Location.FromToken(int_type_expr, stream=self._stream),
            name=int_type_expr.value,
            type=IntType
        ).eval(self._module)

        return CBITFIELD.build_type(
            location=location,
            mod=mod,
            bits=int_type.bits,
            signed=int_type.signed,
            field_size=field_size.value
        )

    def c_block_function_type_expr(self, parts):
        debug('ast_builder', f'c_block_function_type_expr: {parts}')
        cfn = parts.pop(0)
        location = Location.FromToken(cfn, stream=self._stream)

        return CBLOCKFN.build_type(
            location=location,
            return_type=(
                parts.pop(-1)
                if parts and not isinstance(parts[-1], SylvaField) else None
            ),
            parameters=parts,
        )

    def c_function_decl(self, parts):
        debug('ast_builder', f'c_function_decl: {parts}')
        cfn = parts.pop(0)
        name = parts.pop(0)
        location = Location.FromToken(cfn, stream=self._stream)

        cfn_def = SylvaDef(
            location=location,
            name=name.value,
            value=CFnValue(
                location=location,
                type=CFN.build_type(
                    location=location,
                    return_type=( # yapf: ignore
                        parts.pop(-1)
                        if parts and not isinstance(parts[-1], SylvaField)
                        else None
                    ),
                    parameters=parts,
                ),
                value=None
            )
        )

        self._module.add_def(cfn_def)

        return cfn_def

    def c_function_type_expr(self, parts):
        debug('ast_builder', f'c_function_type_expr: {parts}')
        cfn = parts.pop(0)
        location = Location.FromToken(cfn, stream=self._stream)

        return CFN.build_type(
            location=location,
            return_type=(
                parts.pop(-1)
                if parts and not isinstance(parts[-1], SylvaField) else None
            ),
            parameters=parts,
        )

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

    def c_pointer_type_literal_expr(self, parts):
        debug('ast_builder', f'c_pointer_type_expr: {parts}')
        cptr = parts.pop(0)
        ref_type = parts.pop(0)
        mut = bool(parts)
        location = Location.FromToken(cptr, stream=self._stream)

        return CPTR.build_type(
            location=location,
            mod=TypeModifier.CMut if mut else TypeModifier.NoMod,
            referenced_type=ref_type,
        )

    def c_struct_type_def(self, parts):
        debug('ast_builder', f'c_struct_type_def: {parts}')
        cstruct = parts.pop(0)
        name = parts.pop(0).value
        location = Location.FromToken(cstruct, stream=self._stream)

        cstruct_type = CSTRUCT.build_type(location=location)

        for field in parts:
            if not isinstance(field, UndefinedSymbol):
                cstruct_type.fields.append(field)
                continue

            if field.name == name:
                cstruct_type.fields.append(
                    SylvaField(
                        location=field.location, name=name, type=cstruct_type
                    )
                )

            raise errors.UndefinedSymbol(
                location=field.location, name=field.name
            )

        type_def = TypeDef(
            location=location,
            name=name,
            type=CSTRUCT.build_type(location=location, fields=parts),
        )

        self._module.add_def(type_def)

        return type_def

    def c_union_type_def(self, parts):
        debug('ast_builder', f'c_union_type_def: {parts}')
        cunion = parts.pop(0)
        name = parts.pop(0).value
        location = Location.FromToken(cunion, stream=self._stream)

        type_def = TypeDef(
            location=location,
            name=name,
            type=CUNION.build_type(location=location, fields=parts),
        )

        self._module.add_def(type_def)

        return type_def

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

    def c_void_type_literal_expr(self, parts):
        debug('ast_builder', f'c_void_type_literal_expr: {parts}')
        return CVOIDEX if len(parts) == 2 else CVOID

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
        return CodeBlock(
            location=Location.FromToken(parts[0], stream=self._stream),
            code=parts[1:-1]
        )

    def const_def(self, parts):
        debug('ast_builder', f'const_def: {parts}')
        const, name_token, value = parts

        const_def = SylvaDef(
            location=Location.FromToken(const, stream=self._stream),
            name=name_token.value,
            value=value
        )

        self._module.add_def(const_def)

        return const_def

    def default_block(self, parts):
        debug('ast_builder', f'match_case_block: {parts}')
        return DefaultBlock(
            location=Location.FromToken(parts[0], stream=self._stream),
            code=parts[1]
        )

    def expr(self, parts):
        debug('ast_builder', f'expr: {parts}')
        mod, expr = TypeModifier.separate_type_mod(parts)
        expr.type.mod = mod

        return expr

    def function_type_def(self, parts):
        debug('ast_builder', f'function_type_def: {parts}')
        location = Location.FromToken(parts.pop(0), stream=self._stream)

        type_def = TypeDef(
            location=location,
            name=parts.pop(0).value,
            type=FN.build_type(
                location=location,
                parameters=parts[1].children[:-1],
                return_type=parts[1].children[-1],
            )
        )

        self._module.add_def(type_def)

        return type_def

    def function_def(self, parts):
        debug('ast_builder', f'function_def: {parts}')

        fn = parts.pop(0)
        name = parts.pop(0).value
        code_block = parts.pop(-1)
        return_type = ( # yapf: ignore
            parts.pop(-1)
            if parts and not isinstance(parts[-1], SylvaField)
            else None
        )

        location = Location.FromToken(fn, stream=self._stream)

        function_def = SylvaDef(
            name=name,
            value=FnValue(
                location=location,
                type=FN.build_type(
                    location=location,
                    parameters=parts,
                    return_type=return_type
                ),
                value=code_block
            ),
        )

        self._module.add_def(function_def)

        return function_def

    def function_type_literal_expr(self, parts):
        debug('ast_builder', f'function_type_literal_expr: {parts}')

        return FN.build_type(
            location=Location.FromToken(parts.pop(0), stream=self._stream),
            return_type=( # yapf: ignore
                parts.pop(-1)
                if parts and isinstance(parts[-1], SylvaField)
                else None
            ),
            parameters=parts
        )

    def int_expr(self, parts):
        debug('ast_builder', f'int_expr: {parts}')
        int_token = parts[0].children[0]

        return IntValue.FromString(
            location=Location.FromToken(int_token, stream=self._stream),
            strval=int_token.value
        )

    def int_literal_expr(self, parts):
        debug('ast_builder', f'int_literal_expr: {parts}')
        int_token = parts[0]

        return IntLiteralExpr.FromString(
            location=Location.FromToken(int_token, stream=self._stream),
            strval=int_token.value
        )

    @lark.visitors.v_args(tree=True)
    def lookup_expr(self, tree):
        debug('ast_builder', f'lookup_expr: {tree}')
        name = tree.children.pop(0)
        location = Location.FromToken(name, stream=self._stream)

        if (hasattr(tree.meta, 'self_referential_field_names') and
                name in tree.meta.self_referential_field_names):
            value = SelfReferentialField(location=location, name=name.value)
        elif (hasattr(tree.meta, 'function_parameters') and
              name in tree.meta.function_parameters):
            param = tree.meta.function_parameters[name]
            if param.data.value == 'type_param_pair':
                param_name = param.children[0]
                param_type_mod, param_type_expr = (
                    TypeModifier.separate_type_mod(param.children[1:])
                )
                param_loc = Location.FromToken(param_name, stream=self._stream)
            else:
                param_name = None
                param_type_mod, param_type_expr = (
                    TypeModifier.separate_type_mod(
                        param.children
                    )
                )
                param_loc = Location.FromTree(
                    param_type_expr, stream=self._stream
                )

            param_type_expr = param_type_expr[0]

            if param_type_expr.data.value == 'type_placeholder':
                param_type = TypePlaceholder(
                    location=Location.FromTree(
                        param_type_expr, stream=self._stream
                    ),
                    name=param_type_expr.children[0].value,
                )
            else:
                mod, rest = TypeModifier.separate_type_mod(
                    param_type_expr.children
                )
                param_type = LookupExpr(
                    location=Location.FromToken(rest[0], stream=self._stream),
                    name=rest[0].value,
                    type=SylvaType,
                ).eval(self._module)
                param_type.mod = mod
            value = LookupExpr(
                location=param_loc, name=param_name.value, type=param_type
            )
        else:
            value = LookupExpr(
                location=location, name=name.value, type=SylvaType
            ).eval(self._module)

        while tree.children:
            reflection = tree.children.pop(0).value == '::'
            attr_name = tree.children.pop(0)

            value = AttributeLookupExpr(
                location=Location.FromToken(attr_name, stream=self._stream),
                name=attr_name.value,
                obj=value,
                reflection=reflection,
                type=None
            ).eval(self._module)

        return value

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

    def string_literal_expr(self, parts):
        debug('ast_builder', f'string_literal_expr: {parts}')

        return StrLiteralExpr.FromString(
            location=Location.FromToken(parts[0], stream=self._stream),
            strval=parts[0].value[1:-1]
        )

    def string_expr(self, parts):
        debug('ast_builder', f'string_expr: {parts}')
        str_token = parts[0].children[0]
        location = Location.FromToken(str_token, stream=self._stream)

        return StrValue(
            location=Location.FromToken(str_token, stream=self._stream),
            value=str_token.value[1:-1],
            type=STR.build_type(
                location=location,
                element_count=IntValue.FromValue(
                    n=len(str_token.value) - 2,
                    signed=False,
                    location=location,
                )
            )
        )

    def type_def(self, parts):
        debug('ast_builder', f'type_def: {parts}')
        typedef, name, type = parts

        type_def = TypeDef(
            location=Location.FromToken(typedef, stream=self._stream),
            name=name.value,
            type=type,
        )

        self._module.add_def(type_def)

        return type_def

    def type_param_pair(self, parts):
        debug('ast_builder', f'type_param_pair: {parts}')
        name = parts.pop(0)

        mod, rest = TypeModifier.separate_type_mod(parts)
        type = rest[0]
        type.mod = mod

        return SylvaField(
            location=Location.FromToken(name, stream=self._stream),
            name=name.value,
            type=type
        )

    def type_placeholder(self, parts):
        debug('ast_builder', f'type_placeholder: {parts}')
        name = parts.pop(0)
        return TypePlaceholder(
            location=Location.FromToken(name, stream=self._stream),
            name=name.value
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

    def var_type_expr(self, parts):
        debug('ast_builder', f'var_type_expr: {parts}')
        mod, parts = TypeModifier.separate_type_mod(parts)
        type = parts[0].eval(self._module)

        type.mod = mod

        return type

    def variant_type_def(self, parts):
        debug('ast_builder', f'variant_type_def: {parts}')
        variant = parts.pop(0)
        name = parts.pop(0)
        location = Location.FromToken(variant, stream=self._stream)

        type_def = TypeDef(
            location=location,
            name=name.value,
            type=VARIANT.build_type(location=location, fields=parts),
        )

        self._module.add_def(type_def)

        return type_def
