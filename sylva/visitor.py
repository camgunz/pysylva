from dataclasses import dataclass, field

from sylva import errors
from sylva.builtins import (
    ArrayValue,
    BoolType,
    BoolValue,
    CArrayValue,
    CBitFieldType,
    CBitFieldValue,
    CFnValue,
    CPtrValue,
    CStrType,
    CStrValue,
    CStructValue,
    CUnionValue,
    CVoidType,
    CVoidValue,
    CodeBlock,
    EnumValue,
    FloatType,
    FloatValue,
    FnValue,
    Impl,
    IntType,
    IntValue,
    MonoArrayType,
    MonoCArrayType,
    MonoCBlockFnType,
    MonoCFnType,
    MonoCPtrType,
    MonoCStructType,
    MonoCUnionType,
    MonoEnumType,
    MonoFnType,
    MonoStrType,
    MonoStructType,
    MonoVariantType,
    RangeType,
    RangeValue,
    RuneType,
    RuneValue,
    StrValue,
    StringType,
    StringValue,
    StructValue,
    SylvaDef,
    SylvaField,
    SylvaObject,
    SylvaType,
    SylvaValue,
    Type,
    TypeDef,
    TypePlaceholder,
    VariantValue,
)
from sylva.expr import (
    AttributeLookupExpr,
    BinaryExpr,
    BoolExpr,
    BoolLiteralExpr,
    CPtrExpr,
    CVoidExpr,
    CallExpr,
    FloatExpr,
    FloatLiteralExpr,
    IntExpr,
    IntLiteralExpr,
    LiteralExpr,
    LookupExpr,
    RuneExpr,
    RuneLiteralExpr,
    StrExpr,
    StrLiteralExpr,
    StringExpr,
    UnaryExpr,
    VariantFieldTypeLookupExpr,
)
from sylva.mod import Mod
from sylva.scope import Scope
from sylva.stmt import (
    AssignStmt,
    BreakStmt,
    ContinueStmt,
    DefaultBlock,
    IfBlock,
    LetStmt,
    LoopBlock,
    MatchBlock,
    MatchCaseBlock,
    ReturnStmt,
    WhileBlock,
)


@dataclass(kw_only=True)
class BaseVisitor:

    def _call_action(
        self,
        action_name: str,
        obj: SylvaObject | Mod,
        obj_name: str | None,
        parents: list[Mod | SylvaObject | Mod] | None = None
    ) -> bool:
        parents = parents if parents is not None else []
        if func := getattr(self, action_name, None):
            return func(obj, obj_name, parents)
        return True

    def _walk(
        self,
        obj: SylvaObject | Mod | None,
        name: str | None = None,
        parents: list[Mod | SylvaObject | Mod] | None = None,
    ):
        parents = parents if parents else []

        match obj:
            case Mod():
                if not self._call_action('enter_mod', obj, name, parents):
                    return
                with obj.def_listener() as defs:
                    while not defs.empty():
                        d = defs.get()
                        match d:
                            case SylvaDef():
                                if not self._call_action(
                                    'enter_def', obj, name, parents
                                ):
                                    return
                                self._walk(d.value, d.name, parents + [obj])
                                if not self._call_action(
                                    'exit_def', obj, name, parents
                                ):
                                    return
                            case TypeDef():
                                if not self._call_action(
                                    'enter_type_def', d, name, parents
                                ):
                                    return
                                self._walk(d.type, d.name, parents + [obj])
                                for impl in d.type.impls:
                                    self._walk(
                                        impl,
                                        d.type.name,
                                        parents + [obj, d.type]
                                    )
                                if not self._call_action(
                                    'exit_type_def', d, name, parents
                                ):
                                    return
                if not self._call_action('exit_mod', obj, name, parents):
                    return
            case SylvaField():
                if not self._call_action('enter_field', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_field', obj, name, parents):
                    return
            case Impl():
                if not self._call_action('enter_impl', obj, name, parents):
                    return
                for fn in obj.functions.values():
                    self._walk(fn, fn.name, parents + [obj])
                if not self._call_action('exit_impl', obj, name, parents):
                    return
            case Type():
                if not self._call_action('enter_type', obj, name, parents):
                    return
                if not self._call_action('exit_type', obj, name, parents):
                    return
            case BoolType():
                if not self._call_action('enter_bool_type', obj, name, parents):
                    return
                if not self._call_action('exit_bool_type', obj, name, parents):
                    return
            case BoolValue():
                if not self._call_action('enter_bool', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_bool', obj, name, parents):
                    return
            case MonoCPtrType():
                if not self._call_action('enter_c_ptr_type', obj, name, parents):
                    return
                self._walk(
                    obj.referenced_type, name=None, parents=parents + [obj]
                )
                if not self._call_action('exit_c_ptr_type', obj, name, parents):
                    return
            case CPtrValue():
                if not self._call_action('enter_c_ptr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_c_ptr', obj, name, parents):
                    return
            case CStrType():
                if not self._call_action('enter_c_str_type', obj, name, parents):
                    return
                if not self._call_action('exit_c_str_type', obj, name, parents):
                    return
            case CStrValue():
                if not self._call_action('enter_c_str', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_c_str', obj, name, parents):
                    return
            case CVoidType():
                if not self._call_action('enter_c_void_type', obj, name, parents):
                    return
                if not self._call_action('exit_c_void_type', obj, name, parents):
                    return
            case CVoidValue():
                if not self._call_action('enter_c_void', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_c_void', obj, name, parents):
                    return
            case MonoEnumType():
                if not self._call_action('enter_enum_type', obj, name, parents):
                    return
                for value in obj.values.values():
                    self._walk(value, name=None, parents=parents + [obj])
                if not self._call_action('exit_enum_type', obj, name, parents):
                    return
            case EnumValue():
                if not self._call_action('enter_enum', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_enum', obj, name, parents):
                    return
            case CodeBlock():
                if not self._call_action('enter_code_block', obj, name, parents):
                    return
                for node in obj.code:
                    self._walk(node, name=None, parents=parents + [obj])
                if not self._call_action('exit_code_block', obj, name, parents):
                    return
            case MonoFnType():
                if not self._call_action('enter_fn_type', obj, name, parents):
                    return
                for param in obj.parameters:
                    self._walk(param.type, name=None, parents=parents + [obj])
                if obj.return_type:
                    self._walk(
                        obj.return_type, name=None, parents=parents + [obj]
                    )
                if not self._call_action('exit_fn_type', obj, name, parents):
                    return
            case MonoCFnType():
                if not self._call_action('enter_c_fn_type', obj, name, parents):
                    return
                for param in obj.parameters:
                    self._walk(param.type, name=None, parents=parents + [obj])
                if obj.return_type:
                    self._walk(
                        obj.return_type, name=None, parents=parents + [obj]
                    )
                if not self._call_action('exit_c_fn_type', obj, name, parents):
                    return
            case MonoCBlockFnType():
                if not self._call_action('enter_c_block_fn_type', obj, name, parents):
                    return
                for param in obj.parameters:
                    self._walk(param.type, name=None, parents=parents + [obj])
                if obj.return_type:
                    self._walk(
                        obj.return_type, name=None, parents=parents + [obj]
                    )
                if not self._call_action('exit_c_block_fn_type', obj, name, parents):
                    return
            case FnValue():
                if not self._call_action('enter_fn', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                self._walk(obj.value, name=None, parents=parents + [obj])
                if not self._call_action('exit_fn', obj, name, parents):
                    return
            case CFnValue():
                if not self._call_action('enter_c_fn', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                self._walk(obj.value, name=None, parents=parents + [obj])
                if not self._call_action('exit_c_fn', obj, name, parents):
                    return
            case RuneType():
                if not self._call_action('enter_rune_type', obj, name, parents):
                    return
                if not self._call_action('exit_rune_type', obj, name, parents):
                    return
            case RuneValue():
                if not self._call_action('enter_rune', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_rune', obj, name, parents):
                    return
            # case ComplexType():
            #     self._call_action('enter_complex_type', obj, name, parents)
            # case ComplexValue():
            #     self._call_action('enter_complex', obj, name, parents)
            #     self._walk(obj.type, name=None, parents=parents + [obj])
            case FloatType():
                if not self._call_action('enter_float_type', obj, name, parents):
                    return
                if not self._call_action('exit_float_type', obj, name, parents):
                    return
            case FloatValue():
                if not self._call_action('enter_float', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_float', obj, name, parents):
                    return
            case IntType():
                if not self._call_action('enter_int_type', obj, name, parents):
                    return
                if not self._call_action('exit_int_type', obj, name, parents):
                    return
            case IntValue():
                if not self._call_action('enter_int', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_int', obj, name, parents):
                    return
            case RangeType():
                if not self._call_action('enter_range', obj, name, parents):
                    return
                if not self._call_action('exit_range', obj, name, parents):
                    return
            case RangeValue():
                if not self._call_action('enter_range_value', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_range_value', obj, name, parents):
                    return
            case MonoCArrayType():
                if not self._call_action('enter_c_array_type', obj, name, parents):
                    return
                self._walk(obj.element_type, name=None, parents=parents + [obj])
                self._walk(
                    obj.element_count, name=None, parents=parents + [obj]
                )
                if not self._call_action('exit_c_array_type', obj, name, parents):
                    return
            case CArrayValue():
                if not self._call_action('enter_c_array_value', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_c_array_value', obj, name, parents):
                    return
            case CBitFieldType():
                if not self._call_action('enter_c_bit_field_type', obj, name, parents):
                    return
                if not self._call_action('exit_c_bit_field_type', obj, name, parents):
                    return
            case CBitFieldValue():
                if not self._call_action('enter_c_bit_field_value', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_c_bit_field_value', obj, name, parents):
                    return
            case MonoStructType():
                if not self._call_action('enter_struct_type', obj, name, parents):
                    return
                if not self._call_action('exit_struct_type', obj, name, parents):
                    return
            case StructValue():
                if not self._call_action('enter_struct', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_struct', obj, name, parents):
                    return
            case MonoVariantType():
                if not self._call_action('enter_variant_type', obj, name, parents):
                    return
                if not self._call_action('exit_variant_type', obj, name, parents):
                    return
            case VariantValue():
                if not self._call_action('enter_variant', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_variant', obj, name, parents):
                    return
            case MonoCStructType():
                if not self._call_action('enter_c_struct_type', obj, name, parents):
                    return
                if not self._call_action('exit_c_struct_type', obj, name, parents):
                    return
            case CStructValue():
                if not self._call_action('enter_c_struct', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_c_struct', obj, name, parents):
                    return
            case MonoCUnionType():
                if not self._call_action('enter_c_union_type', obj, name, parents):
                    return
                if not self._call_action('exit_c_union_type', obj, name, parents):
                    return
            case CUnionValue():
                if not self._call_action('enter_c_union', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_c_union', obj, name, parents):
                    return
            case MonoStrType():
                if not self._call_action('enter_str_type', obj, name, parents):
                    return
                if not self._call_action('exit_str_type', obj, name, parents):
                    return
            case StrValue():
                if not self._call_action('enter_str', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_str', obj, name, parents):
                    return
            case StringType():
                if not self._call_action('enter_string_type', obj, name, parents):
                    return
                if not self._call_action('exit_string_type', obj, name, parents):
                    return
            case StringValue():
                if not self._call_action('enter_string', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_string', obj, name, parents):
                    return
            case MonoArrayType():
                if not self._call_action('enter_array_type', obj, name, parents):
                    return
                self._walk(obj.element_type, name=None, parents=parents + [obj])
                self._walk(
                    obj.element_count, name=None, parents=parents + [obj]
                )
                if not self._call_action('exit_array_type', obj, name, parents):
                    return
            case ArrayValue():
                if not self._call_action('enter_array_value', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_array_value', obj, name, parents):
                    return
            case TypePlaceholder():
                if not self._call_action('enter_type_placeholder', obj, name, parents):
                    return
                if not self._call_action('exit_type_placeholder', obj, name, parents):
                    return
            case LetStmt():
                if not self._call_action('enter_let_stmt', obj, name, parents):
                    return
                self._walk(obj.expr, name=None, parents=parents + [obj])
                if not self._call_action('exit_let_stmt', obj, name, parents):
                    return
            case AssignStmt():
                if not self._call_action('enter_assign_stmt', obj, name, parents):
                    return
                self._walk(obj.expr, name=None, parents=parents + [obj])
                if not self._call_action('exit_assign_stmt', obj, name, parents):
                    return
            case BreakStmt():
                if not self._call_action('enter_break_stmt', obj, name, parents):
                    return
                if not self._call_action('exit_break_stmt', obj, name, parents):
                    return
            case ContinueStmt():
                if not self._call_action('enter_continue_stmt', obj, name, parents):
                    return
                if not self._call_action('exit_continue_stmt', obj, name, parents):
                    return
            case ReturnStmt():
                if not self._call_action('enter_return_stmt', obj, name, parents):
                    return
                self._walk(obj.expr, name=None, parents=parents + [obj])
                if not self._call_action('exit_return_stmt', obj, name, parents):
                    return
            case IfBlock():
                if not self._call_action('enter_if_block', obj, name, parents):
                    return
                self._walk(
                    obj.conditional_expr, name=None, parents=parents + [obj]
                )
                self._walk(obj.else_code, name=None, parents=parents + [obj])
                if not self._call_action('exit_if_block', obj, name, parents):
                    return
            case LoopBlock():
                if not self._call_action('enter_loop_block', obj, name, parents):
                    return
                self._walk(obj.code, name=None, parents=parents + [obj])
                if not self._call_action('exit_loop_block', obj, name, parents):
                    return
            case WhileBlock():
                if not self._call_action('enter_while_block', obj, name, parents):
                    return
                self._walk(
                    obj.conditional_expr, name=None, parents=parents + [obj]
                )
                self._walk(obj.code, name=None, parents=parents + [obj])
                if not self._call_action('exit_while_block', obj, name, parents):
                    return
            case MatchCaseBlock():
                if not self._call_action('enter_match_case_block', obj, name, parents):
                    return
                self._walk(
                    obj.variant_field_type_lookup_expr, name, parents + [obj]
                )
                self._walk(obj.code, name=None, parents=parents + [obj])
                if not self._call_action('exit_match_case_block', obj, name, parents):
                    return
            case DefaultBlock():
                if not self._call_action('enter_default_block', obj, name, parents):
                    return
                self._walk(obj.code, name=None, parents=parents + [obj])
                if not self._call_action('exit_default_block', obj, name, parents):
                    return
            case MatchBlock():
                if not self._call_action('enter_match_block', obj, name, parents):
                    return
                self._walk(obj.variant_expr, name=None, parents=parents + [obj])
                for match_case in obj.match_cases:
                    self._walk(match_case, name=None, parents=parents + [obj])
                if obj.default_case:
                    self._walk(
                        obj.default_case, name=None, parents=parents + [obj]
                    )
                if not self._call_action('exit_match_block', obj, name, parents):
                    return
            case LookupExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_lookup_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_lookup_expr', obj, name, parents):
                    return
            case LiteralExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_literal_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'exit_literal_expr', obj, name, parents
                ):
                    return
            case UnaryExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_unary_expr', obj, name, parents):
                    return
                self._walk(obj.expr, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_unary_expr', obj, name, parents):
                    return
            case BinaryExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'enter_binary_expr', obj, name, parents
                ):
                    return
                self._walk(obj.lhs, name=None, parents=parents + [obj])
                self._walk(obj.rhs, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_binary_expr', obj, name, parents):
                    return
            case AttributeLookupExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'enter_attribute_lookup_expr', obj, name, parents
                ):
                    return
                self._walk(obj.obj, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'exit_attribute_lookup_expr', obj, name, parents
                ):
                    return
            case CallExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_call_expr', obj, name, parents):
                    return
                self._walk(obj.function, name=None, parents=parents + [obj])
                for arg in obj.arguments:
                    self._walk(arg, name=None, parents=parents + [obj])
                    if not self._call_action('exit_expr', obj, name, parents):
                        return
                if not self._call_action('exit_call_expr', obj, name, parents):
                    return
            case BoolExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_bool_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_bool_expr', obj, name, parents):
                    return
            case RuneExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_rune_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_rune_expr', obj, name, parents):
                    return
            # case ComplexExpr():
            #     if not self._call_action(
            #         'enter_complex_expr', obj, name, parents
            #     ):
            #         return
            #     self._walk(obj.type, name=None, parents=parents + [obj])
            #     if not self._call_action(
            #         'exit_complex_expr', obj, name, parents
            #     ):
            #         return
            case FloatExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_float_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_float_expr', obj, name, parents):
                    return
            case IntExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_int_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_int_expr', obj, name, parents):
                    return
            case StrExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_str_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_str_expr', obj, name, parents):
                    return
            case StringExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_string_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_string_expr', obj, name, parents):
                    return
            case CPtrExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_c_ptr_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_c_ptr_expr', obj, name, parents):
                    return
            case CVoidExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action('enter_c_void_expr', obj, name, parents):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action('exit_c_void_expr', obj, name, parents):
                    return
            case BoolLiteralExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'enter_bool_literal_expr', obj, name, parents
                ):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'exit_bool_literal_expr', obj, name, parents
                ):
                    return
            case RuneLiteralExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'enter_rune_literal_expr', obj, name, parents
                ):
                    return
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'exit_rune_literal_expr', obj, name, parents
                ):
                    return
            # case ComplexLiteralExpr():
            #     self._call_action(
            #         'enter_complex_literal_expr', obj, name, parents
            #     )
            #     self._walk(obj.type, name=None, parents=parents + [obj])
            #     self._call_action(
            #         'exit_complex_literal_expr', obj, name, parents
            #     )
            case FloatLiteralExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                self._call_action(
                    'enter_float_literal_expr', obj, name, parents
                )
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                self._call_action(
                    'exit_float_literal_expr', obj, name, parents
                )
            case IntLiteralExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                self._call_action(
                    'enter_int_literal_expr', obj, name, parents
                )
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'exit_int_literal_expr', obj, name, parents
                ):
                    return
            case StrLiteralExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                self._call_action(
                    'enter_str_literal_expr', obj, name, parents
                )
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'exit_str_literal_expr', obj, name, parents
                ):
                    return
            case VariantFieldTypeLookupExpr():
                if not self._call_action('enter_expr', obj, name, parents):
                    return
                self._call_action(
                    'enter_variant_field_type_lookup_expr', obj, name, parents
                )
                self._walk(obj.type, name=None, parents=parents + [obj])
                if not self._call_action('exit_expr', obj, name, parents):
                    return
                if not self._call_action(
                    'exit_variant_field_type_lookup_expr', obj, name, parents
                ):
                    return

    def visit(self, module: Mod):
        self._walk(module, module.name, [])


@dataclass(kw_only=True)
class Visitor(BaseVisitor):
    module: Mod | None = field(init=False, default=None)
    funcs: list[FnValue] = field(init=False, default_factory=list)
    scopes: Scope = field(init=False, default_factory=Scope)

    @property
    def current_func(self):
        if not self.funcs:
            raise Exception('Not within a function')
        return self.funcs[0]

    def define(self, name: str, type: SylvaType):
        self.scopes.define(name, type)

    def lookup(self, name: str):
        t = self.scopes.lookup(name)
        if t is not None:
            return t

        if self.module is None:
            raise Exception('self.module is somehow none')

        val = self.module.lookup(name)
        if val is None:
            return None

        match val:
            case Mod():
                return Mod # [NOTE] WTF haha
            case SylvaValue(type=t):
                return t
            case SylvaType():
                return val

    def reset(self):
        self.funcs = []
        self.scopes = Scope()

    def enter_code_block(
        self,
        code_block: CodeBlock,
        name: str,
        parents: list[SylvaObject | Mod]
    ):
        self.scopes.push()
        return True

    def exit_code_block(
        self,
        code_block: CodeBlock,
        name: str,
        parents: list[SylvaObject | Mod]
    ):
        self.scopes.pop()
        return True

    def enter_default_block(
        self,
        default_block: DefaultBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.push()
        return True

    def exit_default_block(
        self,
        default_block: DefaultBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.pop()
        return True

    def enter_fn(self, fn: FnValue, name: str, parents: list[SylvaObject | Mod]):
        self.funcs.append(fn)
        self.scopes.push()
        for param in fn.type.parameters:
            if isinstance(param.type, SylvaType):
                self.define(param.name, param.type)
        return True

    def exit_fn(self, fn: FnValue, name: str, parents: list[SylvaObject | Mod]):
        self.funcs.pop()
        self.scopes.pop()
        return True

    def enter_if_block(
        self,
        if_block: IfBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.push()
        return True

    def exit_if_block(
        self,
        if_block: IfBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.pop()
        return True

    def enter_let_stmt(
        self,
        let_stmt: LetStmt,
        name: str,
        parents: list[SylvaObject | Mod]
    ):
        if let_stmt.expr.type is not None:
            self.define(let_stmt.name, let_stmt.expr.type)
        return True

    def enter_loop_block(
        self,
        loop_block: LoopBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.push()
        return True

    def exit_loop_block(
        self,
        loop_block: LoopBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.pop()
        return True

    def enter_match_block(
        self,
        match_block: MatchBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.push()
        return True

    def exit_match_block(
        self,
        match_block: MatchBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.pop()
        return True

    def enter_match_case_block(
        self,
        match_case_block: MatchCaseBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        match_block = parents[-1]

        if not isinstance(match_block, MatchBlock):
            raise TypeError('Match case block without match block')

        matching_variant_fields = [
            f for f in match_block.variant_expr.type.fields # type: ignore
            if f.name == match_case_block.variant_field_type_lookup_expr.name
        ]
        if not matching_variant_fields:
            raise errors.NoSuchVariantField(
                match_case_block.variant_field_type_lookup_expr.location,
                match_case_block.variant_name,
                match_case_block.variant_field_type_lookup_expr.name,
            )

        variant_field = matching_variant_fields[0]

        self.define(match_case_block.variant_name, variant_field.type)
        self.scopes.push()
        return True

    def exit_match_case_block(
        self,
        match_case_block: MatchCaseBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.pop()
        return True

    def enter_mod(
        self,
        module: Mod,
        name: str,
        parents: list[SylvaObject | Mod]
    ):
        self.module = module
        self.reset()
        return True

    def enter_while_block(
        self,
        while_block: WhileBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.push()
        return True

    def exit_while_block(
        self,
        while_block: WhileBlock,
        name: str,
        parents: list[SylvaObject | Mod],
    ):
        self.scopes.pop()
        return True
