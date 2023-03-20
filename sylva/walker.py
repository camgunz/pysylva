from dataclasses import dataclass, field
from typing import Any
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
class Walker:
    actions: Any
    parents: list[SylvaObject] = field(init=False, default_factory=list)

    def call_action(
        self,
        action_name: str,
        obj: SylvaObject,
        parents: list[SylvaObject] | None = None
    ):
        parents = parents if parents is not None else []
        if func := getattr(self.actions, action_name, None):
            func(obj, parents)

    def walk(
        self,
        obj: SylvaObject | None,
        parents: list[SylvaObject] | None = None
    ):
        parents = parents if parents else []
        match obj:
            case Mod():
                self.call_action('enter_mod', obj, parents)
                for d in obj.defs.values():
                    match d:
                        case SylvaDef():
                            self.walk(d.value, parents + [obj])
                        case SylvaType():
                            self.walk(d.type, parents + [obj])
                self.call_action('exit_mod', obj, parents)
            case SylvaField():
                self.call_action('enter_field', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_field', obj, parents)
            case Type():
                self.call_action('enter_type', obj, parents)
                self.call_action('exit_type', obj, parents)
            case BoolType():
                self.call_action('enter_bool_type', obj, parents)
                self.call_action('exit_bool_type', obj, parents)
            case BoolValue():
                self.call_action('enter_bool', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_bool', obj, parents)
            case MonoCPtrType():
                self.call_action('enter_c_ptr_type', obj, parents)
                self.walk(obj.referenced_type, parents + [obj])
                self.call_action('exit_c_ptr_type', obj, parents)
            case CPtrValue():
                self.call_action('enter_c_ptr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_c_ptr', obj, parents)
            case CStrType():
                self.call_action('enter_c_str_type', obj, parents)
                self.call_action('exit_c_str_type', obj, parents)
            case CStrValue():
                self.call_action('enter_c_str', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_c_str', obj, parents)
            case CVoidType():
                self.call_action('enter_c_void_type', obj, parents)
                self.call_action('exit_c_void_type', obj, parents)
            case CVoidValue():
                self.call_action('enter_c_void', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_c_void', obj, parents)
            case MonoEnumType():
                self.call_action('enter_enum_type', obj, parents)
                for value in obj.values.values():
                    self.walk(value, parents + [obj])
                self.call_action('exit_enum_type', obj, parents)
            case EnumValue():
                self.call_action('enter_enum', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_enum', obj, parents)
            case CodeBlock():
                self.call_action('enter_code_block', obj, parents)
                for node in obj.code:
                    self.walk(node, parents + [obj])
                self.call_action('exit_code_block', obj, parents)
            case MonoFnType():
                self.call_action('enter_fn_type', obj, parents)
                for param in obj.parameters:
                    self.walk(param.type, parents + [obj])
                if obj.return_type:
                    self.walk(obj.return_type, parents + [obj])
                self.call_action('exit_fn_type', obj, parents)
            case MonoCFnType():
                self.call_action('enter_c_fn_type', obj, parents)
                for param in obj.parameters:
                    self.walk(param.type, parents + [obj])
                if obj.return_type:
                    self.walk(obj.return_type, parents + [obj])
                self.call_action('exit_c_fn_type', obj, parents)
            case MonoCBlockFnType():
                self.call_action('enter_c_block_fn_type', obj, parents)
                for param in obj.parameters:
                    self.walk(param.type, parents + [obj])
                if obj.return_type:
                    self.walk(obj.return_type, parents + [obj])
                self.call_action('exit_c_block_fn_type', obj, parents)
            case FnValue():
                self.call_action('enter_fn', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.walk(obj.value, parents + [obj])
                self.call_action('exit_fn', obj, parents)
            case CFnValue():
                self.call_action('enter_c_fn', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.walk(obj.value, parents + [obj])
                self.call_action('exit_c_fn', obj, parents)
            case RuneType():
                self.call_action('enter_rune_type', obj, parents)
                self.call_action('exit_rune_type', obj, parents)
            case RuneValue():
                self.call_action('enter_rune', obj, parents)
                self.walk(obj.type, parents + [obj])
            # case ComplexType():
            #     self.call_action('enter_complex_type', obj, parents)
            # case ComplexValue():
            #     self.call_action('enter_complex', obj, parents)
            #     self.walk(obj.type, parents + [obj])
                self.call_action('exit_rune', obj, parents)
            case FloatType():
                self.call_action('enter_float_type', obj, parents)
                self.call_action('exit_float_type', obj, parents)
            case FloatValue():
                self.call_action('enter_float', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_float', obj, parents)
            case IntType():
                self.call_action('enter_int_type', obj, parents)
                self.call_action('exit_int_type', obj, parents)
            case IntValue():
                self.call_action('enter_int', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_int', obj, parents)
            case RangeType():
                self.call_action('enter_range', obj, parents)
                self.call_action('exit_range', obj, parents)
            case RangeValue():
                self.call_action('enter_range_value', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_range_value', obj, parents)
            case MonoArrayType():
                self.call_action('enter_array_type', obj, parents)
                self.walk(obj.element_type, parents + [obj])
                self.walk(obj.element_count, parents + [obj])
                self.call_action('exit_array_type', obj, parents)
            case ArrayValue():
                self.call_action('enter_array_value', obj)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_array_value', obj)
            case MonoCArrayType():
                self.call_action('enter_c_array_type', obj, parents)
                self.walk(obj.element_type, parents + [obj])
                self.walk(obj.element_count, parents + [obj])
                self.call_action('exit_c_array_type', obj, parents)
            case CArrayValue():
                self.call_action('enter_c_array_value', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_c_array_value', obj, parents)
            case CBitFieldType():
                self.call_action('enter_c_bit_field_type', obj, parents)
                self.call_action('exit_c_bit_field_type', obj, parents)
            case CBitFieldValue():
                self.call_action('enter_c_bit_field_value', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_c_bit_field_value', obj, parents)
            case MonoStructType():
                self.call_action('enter_struct_type', obj, parents)
                self.call_action('exit_struct_type', obj, parents)
            case StructValue():
                self.call_action('enter_struct', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_struct', obj, parents)
            case MonoVariantType():
                self.call_action('enter_variant_type', obj, parents)
                self.call_action('exit_variant_type', obj, parents)
            case VariantValue():
                self.call_action('enter_variant', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_variant', obj, parents)
            case MonoCStructType():
                self.call_action('enter_c_struct_type', obj, parents)
                self.call_action('exit_c_struct_type', obj, parents)
            case CStructValue():
                self.call_action('enter_c_struct', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_c_struct', obj, parents)
            case MonoCUnionType():
                self.call_action('enter_c_union_type', obj, parents)
                self.call_action('exit_c_union_type', obj, parents)
            case CUnionValue():
                self.call_action('enter_c_union', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_c_union', obj, parents)
            case MonoStrType():
                self.call_action('enter_str_type', obj, parents)
                self.call_action('exit_str_type', obj, parents)
            case StrValue():
                self.call_action('enter_str', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_str', obj, parents)
            case StringType():
                self.call_action('enter_string_type', obj, parents)
                self.call_action('exit_string_type', obj, parents)
            case StringValue():
                self.call_action('enter_string', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_string', obj, parents)
            case TypeDef():
                self.call_action('enter_type_def', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_type_def', obj, parents)
            case TypePlaceholder():
                self.call_action('enter_type_placeholder', obj, parents)
                self.call_action('exit_type_placeholder', obj, parents)
            case LetStmt():
                self.call_action('enter_let_stmt', obj, parents)
                self.walk(obj.expr, parents + [obj])
                self.call_action('exit_let_stmt', obj, parents)
            case AssignStmt():
                self.call_action('enter_assign_stmt', obj, parents)
                self.walk(obj.expr, parents + [obj])
                self.call_action('exit_assign_stmt', obj, parents)
            case BreakStmt():
                self.call_action('enter_break_stmt', obj, parents)
                self.call_action('exit_break_stmt', obj, parents)
            case ContinueStmt():
                self.call_action('enter_continue_stmt', obj, parents)
                self.call_action('exit_continue_stmt', obj, parents)
            case ReturnStmt():
                self.call_action('enter_return_stmt', obj, parents)
                self.walk(obj.expr, parents + [obj])
                self.call_action('exit_return_stmt', obj, parents)
            case IfBlock():
                self.call_action('enter_if_stmt', obj, parents)
                self.walk(obj.conditional_expr, parents + [obj])
                self.walk(obj.else_code, parents + [obj])
                self.call_action('exit_if_stmt', obj, parents)
            case LoopBlock():
                self.call_action('enter_loop_stmt', obj, parents)
                self.walk(obj.code, parents + [obj])
                self.call_action('exit_loop_stmt', obj, parents)
            case WhileBlock():
                self.call_action('enter_while_stmt', obj, parents)
                self.walk(obj.conditional_expr, parents + [obj])
                self.walk(obj.code, parents + [obj])
                self.call_action('exit_while_stmt', obj, parents)
            case MatchCaseBlock():
                self.call_action('enter_match_case_block', obj, parents)
                self.walk(obj.variant_field_type_lookup_expr)
                self.walk(obj.code, parents + [obj])
                self.call_action('exit_match_case_block', obj, parents)
            case DefaultBlock():
                self.call_action('enter_match_case_default_block', obj, parents)
                self.walk(obj.code, parents + [obj])
                self.call_action('exit_match_case_default_block', obj, parents)
            case MatchBlock():
                self.call_action('enter_match', obj, parents)
                self.walk(obj.variant_expr, parents + [obj])
                for match_case in obj.match_cases:
                    self.walk(match_case, parents + [obj])
                if obj.default_case:
                    self.walk(obj.default_case, parents + [obj])
                self.call_action('exit_match', obj, parents)
            case LookupExpr():
                self.call_action('enter_lookup_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_lookup_expr', obj, parents)
            case LiteralExpr():
                self.call_action('enter_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_literal_expr', obj, parents)
            case UnaryExpr():
                self.call_action('enter_unary_expr', obj, parents)
                self.walk(obj.expr, parents + [obj])
                self.call_action('exit_unary_expr', obj, parents)
            case BinaryExpr():
                self.call_action('enter_binary_expr', obj, parents)
                self.walk(obj.lhs, parents + [obj])
                self.walk(obj.rhs, parents + [obj])
                self.call_action('exit_binary_expr', obj, parents)
            case AttributeLookupExpr():
                self.call_action('enter_attribute_lookup_expr', obj, parents)
                self.walk(obj.obj, parents + [obj])
                self.call_action('exit_attribute_lookup_expr', obj, parents)
            case CallExpr():
                self.call_action('enter_call_expr', obj, parents)
                self.walk(obj.function, parents + [obj])
                for arg in obj.arguments:
                    self.walk(arg, parents + [obj])
                self.call_action('exit_call_expr', obj, parents)
            case BoolExpr():
                self.call_action('enter_bool_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_bool_expr', obj, parents)
            case RuneExpr():
                self.call_action('enter_rune_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            # case ComplexExpr():
            #     self.call_action('enter_complex_expr', obj, parents)
            #     self.walk(obj.type, parents + [obj])
                self.call_action('exit_rune_expr', obj, parents)
            case FloatExpr():
                self.call_action('enter_float_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_float_expr', obj, parents)
            case IntExpr():
                self.call_action('enter_int_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_int_expr', obj, parents)
            case StrExpr():
                self.call_action('enter_str_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_str_expr', obj, parents)
            case StringExpr():
                self.call_action('enter_string_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_string_expr', obj, parents)
            case CPtrExpr():
                self.call_action('enter_c_ptr_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_c_ptr_expr', obj, parents)
            case CVoidExpr():
                self.call_action('enter_c_void_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_c_void_expr', obj, parents)
            case BoolLiteralExpr():
                self.call_action('enter_bool_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_bool_literal_expr', obj, parents)
            case RuneLiteralExpr():
                self.call_action('enter_rune_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            # case ComplexLiteralExpr():
            #     self.call_action('enter_complex_literal_expr', obj, parents)
            #     self.walk(obj.type, parents + [obj])
                self.call_action('exit_rune_literal_expr', obj, parents)
            case FloatLiteralExpr():
                self.call_action('enter_float_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_float_literal_expr', obj, parents)
            case IntLiteralExpr():
                self.call_action('enter_int_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_int_literal_expr', obj, parents)
            case StrLiteralExpr():
                self.call_action('enter_str_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.call_action('exit_str_literal_expr', obj, parents)
            case VariantFieldTypeLookupExpr():
                self.call_action(
                    'enter_variant_field_type_lookup_expr', obj, parents
                )
                self.walk(obj.type, parents + [obj])
