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

    def __call_action(
        self,
        action_name: str,
        obj: SylvaObject | Mod,
        obj_name: str | None,
        parents: list[Mod | SylvaObject] | None = None
    ):
        parents = parents if parents is not None else []
        if func := getattr(self, action_name, None):
            func(obj, obj_name, parents)

    def __walk(
        self,
        obj: SylvaObject | Mod | None,
        name: str | None = None,
        parents: list[Mod | SylvaObject] | None = None,
    ):
        parents = parents if parents else []
        match obj:
            case Mod():
                self.__call_action('enter_mod', obj, name, parents)
                for d in obj.defs.values():
                    match d:
                        case SylvaDef():
                            self.__walk(d.value, d.name, parents + [obj])
                        case SylvaType():
                            self.__walk(d.type, d.name, parents + [obj])
                self.__call_action('exit_mod', obj, name, parents)
            case SylvaField():
                self.__call_action('enter_field', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_field', obj, name, parents)
            case Type():
                self.__call_action('enter_type', obj, name, parents)
                self.__call_action('exit_type', obj, name, parents)
            case BoolType():
                self.__call_action('enter_bool_type', obj, name, parents)
                self.__call_action('exit_bool_type', obj, name, parents)
            case BoolValue():
                self.__call_action('enter_bool', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_bool', obj, name, parents)
            case MonoCPtrType():
                self.__call_action('enter_c_ptr_type', obj, name, parents)
                self.__walk(obj.referenced_type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_ptr_type', obj, name, parents)
            case CPtrValue():
                self.__call_action('enter_c_ptr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_ptr', obj, name, parents)
            case CStrType():
                self.__call_action('enter_c_str_type', obj, name, parents)
                self.__call_action('exit_c_str_type', obj, name, parents)
            case CStrValue():
                self.__call_action('enter_c_str', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_str', obj, name, parents)
            case CVoidType():
                self.__call_action('enter_c_void_type', obj, name, parents)
                self.__call_action('exit_c_void_type', obj, name, parents)
            case CVoidValue():
                self.__call_action('enter_c_void', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_void', obj, name, parents)
            case MonoEnumType():
                self.__call_action('enter_enum_type', obj, name, parents)
                for value in obj.values.values():
                    self.__walk(value, name=None, parents=parents + [obj])
                self.__call_action('exit_enum_type', obj, name, parents)
            case EnumValue():
                self.__call_action('enter_enum', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_enum', obj, name, parents)
            case CodeBlock():
                self.__call_action('enter_code_block', obj, name, parents)
                for node in obj.code:
                    self.__walk(node, name=None, parents=parents + [obj])
                self.__call_action('exit_code_block', obj, name, parents)
            case MonoFnType():
                self.__call_action('enter_fn_type', obj, name, parents)
                for param in obj.parameters:
                    self.__walk(param.type, name=None, parents=parents + [obj])
                if obj.return_type:
                    self.__walk(obj.return_type, name=None, parents=parents + [obj])
                self.__call_action('exit_fn_type', obj, name, parents)
            case MonoCFnType():
                self.__call_action('enter_c_fn_type', obj, name, parents)
                for param in obj.parameters:
                    self.__walk(param.type, name=None, parents=parents + [obj])
                if obj.return_type:
                    self.__walk(obj.return_type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_fn_type', obj, name, parents)
            case MonoCBlockFnType():
                self.__call_action('enter_c_block_fn_type', obj, name, parents)
                for param in obj.parameters:
                    self.__walk(param.type, name=None, parents=parents + [obj])
                if obj.return_type:
                    self.__walk(obj.return_type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_block_fn_type', obj, name, parents)
            case FnValue():
                self.__call_action('enter_fn', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__walk(obj.value, name=None, parents=parents + [obj])
                self.__call_action('exit_fn', obj, name, parents)
            case CFnValue():
                self.__call_action('enter_c_fn', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__walk(obj.value, name=None, parents=parents + [obj])
                self.__call_action('exit_c_fn', obj, name, parents)
            case RuneType():
                self.__call_action('enter_rune_type', obj, name, parents)
                self.__call_action('exit_rune_type', obj, name, parents)
            case RuneValue():
                self.__call_action('enter_rune', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
            # case ComplexType():
            #     self.__call_action('enter_complex_type', obj, name, parents)
            # case ComplexValue():
            #     self.__call_action('enter_complex', obj, name, parents)
            #     self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_rune', obj, name, parents)
            case FloatType():
                self.__call_action('enter_float_type', obj, name, parents)
                self.__call_action('exit_float_type', obj, name, parents)
            case FloatValue():
                self.__call_action('enter_float', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_float', obj, name, parents)
            case IntType():
                self.__call_action('enter_int_type', obj, name, parents)
                self.__call_action('exit_int_type', obj, name, parents)
            case IntValue():
                self.__call_action('enter_int', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_int', obj, name, parents)
            case RangeType():
                self.__call_action('enter_range', obj, name, parents)
                self.__call_action('exit_range', obj, name, parents)
            case RangeValue():
                self.__call_action('enter_range_value', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_range_value', obj, name, parents)
            case MonoArrayType():
                self.__call_action('enter_array_type', obj, name, parents)
                self.__walk(obj.element_type, name=None, parents=parents + [obj])
                self.__walk(obj.element_count, name=None, parents=parents + [obj])
                self.__call_action('exit_array_type', obj, name, parents)
            case ArrayValue():
                self.__call_action('enter_array_value', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_array_value', obj, name, parents)
            case MonoCArrayType():
                self.__call_action('enter_c_array_type', obj, name, parents)
                self.__walk(obj.element_type, name=None, parents=parents + [obj])
                self.__walk(obj.element_count, name=None, parents=parents + [obj])
                self.__call_action('exit_c_array_type', obj, name, parents)
            case CArrayValue():
                self.__call_action('enter_c_array_value', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_array_value', obj, name, parents)
            case CBitFieldType():
                self.__call_action(
                    'enter_c_bit_field_type', obj, name, parents
                )
                self.__call_action('exit_c_bit_field_type', obj, name, parents)
            case CBitFieldValue():
                self.__call_action(
                    'enter_c_bit_field_value', obj, name, parents
                )
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action(
                    'exit_c_bit_field_value', obj, name, parents
                )
            case MonoStructType():
                self.__call_action('enter_struct_type', obj, name, parents)
                self.__call_action('exit_struct_type', obj, name, parents)
            case StructValue():
                self.__call_action('enter_struct', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_struct', obj, name, parents)
            case MonoVariantType():
                self.__call_action('enter_variant_type', obj, name, parents)
                self.__call_action('exit_variant_type', obj, name, parents)
            case VariantValue():
                self.__call_action('enter_variant', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_variant', obj, name, parents)
            case MonoCStructType():
                self.__call_action('enter_c_struct_type', obj, name, parents)
                self.__call_action('exit_c_struct_type', obj, name, parents)
            case CStructValue():
                self.__call_action('enter_c_struct', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_struct', obj, name, parents)
            case MonoCUnionType():
                self.__call_action('enter_c_union_type', obj, name, parents)
                self.__call_action('exit_c_union_type', obj, name, parents)
            case CUnionValue():
                self.__call_action('enter_c_union', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_union', obj, name, parents)
            case MonoStrType():
                self.__call_action('enter_str_type', obj, name, parents)
                self.__call_action('exit_str_type', obj, name, parents)
            case StrValue():
                self.__call_action('enter_str', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_str', obj, name, parents)
            case StringType():
                self.__call_action('enter_string_type', obj, name, parents)
                self.__call_action('exit_string_type', obj, name, parents)
            case StringValue():
                self.__call_action('enter_string', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_string', obj, name, parents)
            case TypeDef():
                self.__call_action('enter_type_def', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_type_def', obj, name, parents)
            case TypePlaceholder():
                self.__call_action(
                    'enter_type_placeholder', obj, name, parents
                )
                self.__call_action('exit_type_placeholder', obj, name, parents)
            case LetStmt():
                self.__call_action('enter_let_stmt', obj, name, parents)
                self.__walk(obj.expr, name=None, parents=parents + [obj])
                self.__call_action('exit_let_stmt', obj, name, parents)
            case AssignStmt():
                self.__call_action('enter_assign_stmt', obj, name, parents)
                self.__walk(obj.expr, name=None, parents=parents + [obj])
                self.__call_action('exit_assign_stmt', obj, name, parents)
            case BreakStmt():
                self.__call_action('enter_break_stmt', obj, name, parents)
                self.__call_action('exit_break_stmt', obj, name, parents)
            case ContinueStmt():
                self.__call_action('enter_continue_stmt', obj, name, parents)
                self.__call_action('exit_continue_stmt', obj, name, parents)
            case ReturnStmt():
                self.__call_action('enter_return_stmt', obj, name, parents)
                self.__walk(obj.expr, name=None, parents=parents + [obj])
                self.__call_action('exit_return_stmt', obj, name, parents)
            case IfBlock():
                self.__call_action('enter_if_stmt', obj, name, parents)
                self.__walk(obj.conditional_expr, name=None, parents=parents + [obj])
                self.__walk(obj.else_code, name=None, parents=parents + [obj])
                self.__call_action('exit_if_stmt', obj, name, parents)
            case LoopBlock():
                self.__call_action('enter_loop_stmt', obj, name, parents)
                self.__walk(obj.code, name=None, parents=parents + [obj])
                self.__call_action('exit_loop_stmt', obj, name, parents)
            case WhileBlock():
                self.__call_action('enter_while_stmt', obj, name, parents)
                self.__walk(obj.conditional_expr, name=None, parents=parents + [obj])
                self.__walk(obj.code, name=None, parents=parents + [obj])
                self.__call_action('exit_while_stmt', obj, name, parents)
            case MatchCaseBlock():
                self.__call_action(
                    'enter_match_case_block', obj, name, parents
                )
                self.__walk(
                    obj.variant_field_type_lookup_expr, name, parents + [obj]
                )
                self.__walk(obj.code, name=None, parents=parents + [obj])
                self.__call_action('exit_match_case_block', obj, name, parents)
            case DefaultBlock():
                self.__call_action(
                    'enter_match_case_default_block', obj, name, parents
                )
                self.__walk(obj.code, name=None, parents=parents + [obj])
                self.__call_action(
                    'exit_match_case_default_block', obj, name, parents
                )
            case MatchBlock():
                self.__call_action('enter_match', obj, name, parents)
                self.__walk(obj.variant_expr, name=None, parents=parents + [obj])
                for match_case in obj.match_cases:
                    self.__walk(match_case, name=None, parents=parents + [obj])
                if obj.default_case:
                    self.__walk(obj.default_case, name=None, parents=parents + [obj])
                self.__call_action('exit_match', obj, name, parents)
            case LookupExpr():
                self.__call_action('enter_lookup_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_lookup_expr', obj, name, parents)
            case LiteralExpr():
                self.__call_action('enter_literal_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_literal_expr', obj, name, parents)
            case UnaryExpr():
                self.__call_action('enter_unary_expr', obj, name, parents)
                self.__walk(obj.expr, name=None, parents=parents + [obj])
                self.__call_action('exit_unary_expr', obj, name, parents)
            case BinaryExpr():
                self.__call_action('enter_binary_expr', obj, name, parents)
                self.__walk(obj.lhs, name=None, parents=parents + [obj])
                self.__walk(obj.rhs, name=None, parents=parents + [obj])
                self.__call_action('exit_binary_expr', obj, name, parents)
            case AttributeLookupExpr():
                self.__call_action(
                    'enter_attribute_lookup_expr', obj, name, parents
                )
                self.__walk(obj.obj, name=None, parents=parents + [obj])
                self.__call_action(
                    'exit_attribute_lookup_expr', obj, name, parents
                )
            case CallExpr():
                self.__call_action('enter_call_expr', obj, name, parents)
                self.__walk(obj.function, name=None, parents=parents + [obj])
                for arg in obj.arguments:
                    self.__walk(arg, name=None, parents=parents + [obj])
                self.__call_action('exit_call_expr', obj, name, parents)
            case BoolExpr():
                self.__call_action('enter_bool_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_bool_expr', obj, name, parents)
            case RuneExpr():
                self.__call_action('enter_rune_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
            # case ComplexExpr():
            #     self.__call_action('enter_complex_expr', obj, name, parents)
            #     self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_rune_expr', obj, name, parents)
            case FloatExpr():
                self.__call_action('enter_float_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_float_expr', obj, name, parents)
            case IntExpr():
                self.__call_action('enter_int_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_int_expr', obj, name, parents)
            case StrExpr():
                self.__call_action('enter_str_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_str_expr', obj, name, parents)
            case StringExpr():
                self.__call_action('enter_string_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_string_expr', obj, name, parents)
            case CPtrExpr():
                self.__call_action('enter_c_ptr_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_ptr_expr', obj, name, parents)
            case CVoidExpr():
                self.__call_action('enter_c_void_expr', obj, name, parents)
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_c_void_expr', obj, name, parents)
            case BoolLiteralExpr():
                self.__call_action(
                    'enter_bool_literal_expr', obj, name, parents
                )
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action(
                    'exit_bool_literal_expr', obj, name, parents
                )
            case RuneLiteralExpr():
                self.__call_action(
                    'enter_rune_literal_expr', obj, name, parents
                )
                self.__walk(obj.type, name=None, parents=parents + [obj])
            # case ComplexLiteralExpr():
            #     self.__call_action(
            #         'enter_complex_literal_expr', obj, name, parents
            #     )
            #     self.__walk(obj.type, name=None, parents=parents + [obj])
            #     self.__call_action(
            #         'exit_rune_literal_expr', obj, name, parents
            #     )
            case FloatLiteralExpr():
                self.__call_action(
                    'enter_float_literal_expr', obj, name, parents
                )
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action(
                    'exit_float_literal_expr', obj, name, parents
                )
            case IntLiteralExpr():
                self.__call_action(
                    'enter_int_literal_expr', obj, name, parents
                )
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_int_literal_expr', obj, name, parents)
            case StrLiteralExpr():
                self.__call_action(
                    'enter_str_literal_expr', obj, name, parents
                )
                self.__walk(obj.type, name=None, parents=parents + [obj])
                self.__call_action('exit_str_literal_expr', obj, name, parents)
            case VariantFieldTypeLookupExpr():
                self.__call_action(
                    'enter_variant_field_type_lookup_expr', obj, name, parents
                )
                self.__walk(obj.type, name=None, parents=parents + [obj])

    def visit(self, module: Mod):
        self.__walk(module, module.name, [])


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

    def enter_code_block(
        self,
        code_block: CodeBlock,
        name: str,
        parents: list[SylvaObject]
    ):
        self.scopes.push()

    def exit_code_block(
        self,
        code_block: CodeBlock,
        name: str,
        parents: list[SylvaObject]
    ):
        self.scopes.pop()

    def enter_fn(self, fn: FnValue, name: str, parents: list[SylvaObject]):
        self.funcs.append(fn)
        self.scopes.push()
        for param in fn.type.parameters:
            if isinstance(param.type, SylvaType):
                self.define(param.name, param.type)

    def exit_fn(self, fn: FnValue, name: str, parents: list[SylvaObject]):
        self.funcs.pop()
        self.scopes.pop()

    def enter_let_stmt(
        self,
        let_stmt: LetStmt,
        name: str,
        parents: list[SylvaObject]
    ):
        if let_stmt.expr.type is not None:
            self.define(let_stmt.name, let_stmt.expr.type)

    def enter_match_case_block(
        self,
        match_case_block: MatchCaseBlock,
        name: str,
        parents: list[SylvaObject],
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

    def enter_mod(
        self,
        module: Mod,
        name: str,
        parents: list[SylvaObject]
    ):
        self.module = module
        self.funcs = []
        self.scopes = Scope()
