import lark

from sylva import _SIZE_SIZE
from sylva.builtins import (  # noqa: F403
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
    CBitFieldValue,
    CFN,
    CFnValue,
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
    FloatValue,
    FnValue,
    I128,
    I16,
    I32,
    I64,
    I8,
    IntValue,
    RANGE,
    RUNE,
    RangeValue,
    RuneValue,
    STR,
    STRING,
    STRUCT,
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
    U128,
    U16,
    U32,
    U64,
    U8,
    VARIANT,
    VariantValue,
)
from sylva.code_block import CodeBlock
from sylva.const import (
    ConstAttributeLookupExpr,
    ConstDef,
    ConstLookupExpr,
    ConstReflectionLookupExpr,
)
from sylva.expr import AttributeLookupExpr, CallExpr, ReflectionLookupExpr
from sylva.location import Location


def separate_type_mod(parts: list):
    if not isinstance(parts[0], lark.Token):
        if isinstance(parts[-1], lark.Token) and parts[-1].value == '!':
            return (TypeModifier.CMut, parts[1:-1])

        return (TypeModifier.NoMod, parts)

    first_child = parts[0].value

    if first_child == '*':
        return (TypeModifier.Ptr, parts[1:])

    if not first_child == '&':
        return (TypeModifier.NoMod, parts)

    if isinstance(parts[-1], lark.Token) and parts[-1].value == '!':
        return (TypeModifier.ExRef, parts[1:-1])

    return (TypeModifier.Ref, parts[1:])


def build_int_value(location, raw_value):
    if raw_value.startswith('0b') or raw_value.startswith('0B'):
        base = 2
    elif raw_value.startswith('0o') or raw_value.startswith('0O'):
        base = 8
    elif raw_value.startswith('0x') or raw_value.startswith('0X'):
        base = 16
    else:
        base = 10

    if raw_value.endswith('i'):
        value = int(raw_value[:-1], base)
        if _SIZE_SIZE == 8:
            return IntValue(location=location, type=I8, value=value)
        if _SIZE_SIZE == 16:
            return IntValue(location=location, type=I16, value=value)
        if _SIZE_SIZE == 32:
            return IntValue(location=location, type=I32, value=value)
        if _SIZE_SIZE == 64:
            return IntValue(location=location, type=I64, value=value)
        if _SIZE_SIZE == 128:
            return IntValue(location=location, type=I128, value=value)

    if raw_value.endswith('i8'):
        return IntValue(
            location=location,
            type=I8,
            value=int(raw_value[:-2], base),
        )

    if raw_value.endswith('i16'):
        return IntValue(
            location=location,
            type=I16,
            value=int(raw_value[:-3], base),
        )

    if raw_value.endswith('i32'):
        return IntValue(
            location=location,
            type=I32,
            value=int(raw_value[:-3], base),
        )

    if raw_value.endswith('i64'):
        return IntValue(
            location=location,
            type=I64,
            value=int(raw_value[:-3], base),
        )

    if raw_value.endswith('i128'):
        return IntValue(
            location=location,
            type=I128,
            value=int(raw_value[:-4], base),
        )

    if raw_value.endswith('u'):
        value = int(raw_value[:-1], base)
        if _SIZE_SIZE == 8:
            return IntValue(location=location, type=U8, value=value)
        if _SIZE_SIZE == 16:
            return IntValue(location=location, type=U16, value=value)
        if _SIZE_SIZE == 32:
            return IntValue(location=location, type=U32, value=value)
        if _SIZE_SIZE == 64:
            return IntValue(location=location, type=U64, value=value)
        if _SIZE_SIZE == 128:
            return IntValue(location=location, type=U128, value=value)

    if raw_value.endswith('u8'):
        return IntValue(
            location=location,
            type=I8,
            value=int(raw_value[:-2], base),
        )

    if raw_value.endswith('u16'):
        return IntValue(
            location=location,
            type=I16,
            value=int(raw_value[:-3], base),
        )

    if raw_value.endswith('u32'):
        return IntValue(
            location=location,
            type=I32,
            value=int(raw_value[:-3], base),
        )

    if raw_value.endswith('u64'):
        return IntValue(
            location=location,
            type=I64,
            value=int(raw_value[:-3], base),
        )

    if raw_value.endswith('u128'):
        return IntValue(
            location=location,
            type=I128,
            value=int(raw_value[:-4], base),
        )

    raise ValueError('Malformed int value {raw_value}')


def build_float_value(location, raw_value):
    val = float(raw_value[:-3])

    if raw_value.endswith('f16'):
        return FloatValue(location=location, type=F16, value=val)
    if raw_value.endswith('f32'):
        return FloatValue(location=location, type=F32, value=val)
    if raw_value.endswith('f64'):
        return FloatValue(location=location, type=F64, value=val)
    if raw_value.endswith('f128'):
        return FloatValue(location=location, type=F128, value=val)

    raise ValueError(f'Malformed float value {raw_value}')


def build_complex_value(location, raw_value):
    val = complex(raw_value[:-3])

    if raw_value.endswith('f16'):
        return ComplexValue(location=location, type=C16, value=val)
    if raw_value.endswith('f32'):
        return ComplexValue(location=location, type=C32, value=val)
    if raw_value.endswith('f64'):
        return ComplexValue(location=location, type=C64, value=val)
    if raw_value.endswith('f128'):
        return ComplexValue(location=location, type=C128, value=val)

    raise Exception(f'Malformed complex value {raw_value}')


class ASTBuilder(lark.Transformer):

    def __init__(self, program, module, location):
        super().__init__()
        self._program = program
        self._module = module
        self._location = location
        self._stream = location.stream

    def c_array_type_def(self, parts):
        print('c_array_type_def', parts)
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
        print('c_array_type_literal_expr', parts)
        mod, parts = separate_type_mod(parts)
        carray, element_type, element_count = parts
        location = Location.FromToken(carray, stream=self._stream)

        return CARRAY.build_type(
            location=location,
            mod=mod,
            element_type=element_type,
            element_count=element_count,
        )

    def c_function_decl(self, parts):
        print('c_function_decl', parts)
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

    def expr(self, parts):
        print('expr', parts)
        mod, expr = separate_type_mod(parts)
        expr.type.mod = mod

        return expr

    def c_pointer_expr(self, parts):
        print('c_pointer_expr', parts)
        cptr, atom_expr = parts
        location = Location.FromToken(cptr, stream=self._stream)
        ref_type = atom_expr.eval(self._module)

        return CPtrValue(
            location=location,
            type=CPTR.build_type(
                location=location,
                referenced_type=ref_type,
            ),
            value=None,
        )

    def c_pointer_type_literal_expr(self, parts):
        print('c_pointer_type_expr', parts)
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
        print('c_struct_type_def', parts)
        cstruct = parts.pop(0)
        name = parts.pop(0).value
        location = Location.FromToken(cstruct, stream=self._stream)

        type_def = TypeDef(
            location=location,
            name=name,
            type=CSTRUCT.build_type(location=location, fields=parts),
        )

        self._module.add_def(type_def)

        return type_def

    def c_union_type_def(self, parts):
        print('c_union_type_def', parts)
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
        print('c_void_expr', parts)
        cvoid, expr = parts
        location = Location.FromToken(cvoid, stream=self._stream)
        return CVoidValue(location=location, expr=expr)

    def c_void_type_literal_expr(self, parts):
        print('c_void_type_literal_expr', parts)
        return CVOIDEX if len(parts) == 2 else CVOID

    def call_expr(self, parts):
        print('call_expr', parts)
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
        print('code_block', parts)
        return CodeBlock(code=parts)

    def const_def(self, parts):
        print('const_def', parts)
        const, name_token, value = parts
        return ConstDef(
            location=Location.FromToken(const, stream=self._stream),
            name=name_token.value,
            value=value
        )

    def const_lookup_expr(self, parts):
        print('const_lookup_expr', parts)
        value = ConstLookupExpr(
            location=Location.FromToken(parts[0], stream=self._stream),
            name=parts.pop(0).value,
            type=None
        ).eval(self._module)

        while parts:
            reflection = parts.pop(0).value == '::'
            attr_name = parts.pop(0)
            LookupExprType = (
                ConstReflectionLookupExpr
                if reflection else ConstAttributeLookupExpr
            )

            value = LookupExprType(
                location=Location.FromToken(attr_name, stream=self._stream),
                name=attr_name.value,
                obj=value,
                type=None
            ).eval(self._module)

        return value

    def exrefparam(self, parts):
        print('exrefparam', parts)
        name = parts.pop(0)
        location = Location.FromToken(name, stream=self._stream)
        type = ConstLookupExpr(
            location=location,
            name=name,
            type=SylvaType,
        ).eval(self._module)
        type.mod = TypeModifier.ExRef

        return SylvaField(location=location, name=name, type=type)

    def function_type_def(self, parts):
        print('function_type_def', parts)
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
        print('function_def', parts)

        fn = parts.pop(0)
        name = parts.pop(0).value
        code_block = parts.pop(-1)
        return_type = parts.pop(0) if parts else None

        location = Location.FromToken(fn, stream=self._stream)

        return SylvaDef(
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

    def int_expr(self, parts):
        print('int_expr', parts)
        int_token = parts[0].children[0]

        return build_int_value(
            location=Location.FromToken(int_token, stream=self._stream),
            raw_value=int_token.value
        )

    def int_literal_expr(self, parts):
        print('int_literal_expr', parts)
        int_token = parts[0]

        return build_int_value(
            location=Location.FromToken(int_token, stream=self._stream),
            raw_value=int_token.value
        )

    def lookup_expr(self, parts):
        print('lookup_expr', parts)
        tree = parts[0]
        value = AttributeLookupExpr(
            location=Location.FromToken(parts[0], stream=self._stream),
            name=parts.pop(0).value,
            type=None
        ).eval(self._module)

        while parts:
            reflection = tree.children.pop(0).value == '::'
            attr_name = tree.children.pop(0)
            LookupExprType = (
                ReflectionLookupExpr if reflection else AttributeLookupExpr
            )

            value = LookupExprType(
                location=Location.FromToken(attr_name, stream=self._stream),
                name=attr_name.value,
                obj=value,
                type=None
            )

        return value

    def ptrparam(self, parts):
        print('ptrparam', parts)
        name = parts.pop(0)
        location = Location.FromToken(name, stream=self._stream)
        type = ConstLookupExpr(
            location=location,
            name=name,
            type=SylvaType,
        ).eval(self._module)
        type.mod = TypeModifier.Ptr

        return SylvaField(location=location, name=name, type=type)

    def refparam(self, parts):
        print('refparam', parts)
        name = parts.pop(0)
        location = Location.FromToken(name, stream=self._stream)
        type = ConstLookupExpr(
            location=location,
            name=name,
            type=SylvaType,
        ).eval(self._module)
        type.mod = TypeModifier.Ref

        return SylvaField(location=location, name=name, type=type)

    def string_expr(self, parts):
        print('string_expr', parts)
        str_token = parts[0].children[0]
        location = Location.FromToken(str_token, stream=self._stream)

        return StrValue(
            location=Location.FromToken(str_token, stream=self._stream),
            value=str_token.value[1:-1],
            type=STR.build_type(
                location=location, element_count=len(str_token.value) - 2
            )
        )

    def string_literal_expr(self, parts):
        print('string_literal_expr', parts)
        str_token = parts[0]
        location = Location.FromToken(str_token, stream=self._stream)

        return StrValue(
            location=Location.FromToken(str_token, stream=self._stream),
            value=str_token.value[1:-1],
            type=STR.build_type(
                location=location, element_count=len(str_token.value) - 2
            )
        )

    def type_def(self, parts):
        print('type_def', parts)
        type_def, name, type = parts
        return TypeDef(
            location=Location.FromToken(type_def, stream=self._stream),
            name=name.value,
            type=type,
        )

    def type_param(self, parts):
        print('type_param', parts)
        raise Exception('type_param')

    def type_param_pair(self, parts):
        print('type_param_pair', parts)
        name = parts.pop(0)
        type_param = parts.pop(0)

        if isinstance(type_param, lark.Tree):
            mod, rest = separate_type_mod(type_param.children)
            type = rest[0].eval(self._module)
            type.mod = mod
        else:
            type = type_param

        return SylvaField(
            location=Location.FromToken(name, stream=self._stream),
            name=name.value,
            type=type
        )

    def var_type_expr(self, parts):
        print('var_type_expr', parts)
        mod, parts = separate_type_mod(parts)
        type = parts[0].eval(self._module)

        type.mod = mod

        return type
