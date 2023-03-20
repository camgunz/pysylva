from dataclasses import dataclass, field
from typing import Any


@dataclass(kw_only=True)
class Walker:
    actions: Any
    parents: list[SylvaObject] = field(init=False, default_factory=list)

    @contextmanger
    def add_parent(self, parent: SylvaObject):
        parents.append(parent)
        yield
        parents.pop()

    def call_action(
        self,
        action_name: str,
        obj: SylvaObject,
        parents: Optional[list[SylvaObject]] = None
    ):
        parents = parents if parents is not None else []
        if func := getattr(self.actions, action_name, None):
            func(obj, parents)

    def walk(self, obj: SylvaObject, parents: Optional[list[SylvaObject]] = None):
        parents = parents if parents else []
        match obj:
            case Mod():
                self.call_action('mod', obj, parents)
                for d in obj.defs.values():
                    match d:
                        case SylvaDef():
                            self.walk(d.value, parents + [obj])
                        case SylvaType():
                            self.walk(d.type, parents + [obj])
            case SylvaField():
                self.call_action('field', obj, parents)
                self.walk(obj.type, parents + [obj])
            case Type():
                self.call_action('type', obj, parents)
            case BoolType():
                self.call_action('bool_type', obj, parents)
            case BoolValue():
                self.call_action('bool', obj, parents)
                self.walk(obj.type, parents + [obj])
            case MonoCPtrType():
                self.call_action('c_ptr_type', obj, parents)
                self.walk(obj.referenced_type, parents + [obj])
            case CPtrValue():
                self.call_action('c_ptr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case CStrType():
                self.call_action('c_str_type', obj, parents)
            case CStrValue():
                self.call_action('c_str', obj, parents)
                self.walk(obj.type, parents + [obj])
            case CVoidType():
                self.call_action('c_void_type', obj, parents)
            case CVoidValue():
                self.call_action('c_void', obj, parents)
                self.walk(obj.type, parents + [obj])
            case MonoEnumType():
                self.call_action('enum_type', obj, parents)
                for value in obj.values.values():
                    self.walk(value, parents + [obj])
            case EnumValue():
                self.call_action('enum', obj, parents)
                self.walk(obj.type, parents + [obj])
            case CodeBlock():
                self.call_action('code_block', obj, parents)
                for node in code_block.code:
                    self.walk(node, obj, parents + [obj])
            case MonoFnType():
                self.call_action('fn_type', obj, parents)
                for param in obj.parameters:
                    self.walk(param.type, parents + [obj])
                if obj.return_type:
                    self.walk(obj.return_type, parents + [obj])
            case MonoCFnType():
                self.call_action('c_fn_type', obj, parents)
                for param in obj.parameters:
                    self.walk(param.type, parents + [obj])
                if obj.return_type:
                    self.walk(obj.return_type, parents + [obj])
            case MonoCBlockFnType():
                self.call_action('c_block_fn_type', obj, parents)
                for param in obj.parameters:
                    self.walk(param.type, parents + [obj])
                if obj.return_type:
                    self.walk(obj.return_type, parents + [obj])
            case FnValue():
                self.call_action('fn', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.walk(obj.value, parents + [obj])
            case CFnValue():
                self.call_action('c_fn', obj, parents)
                self.walk(obj.type, parents + [obj])
                self.walk(obj.value, parents + [obj])
            case RuneType():
                self.call_action('rune_type', obj, parents)
            case RuneValue():
                self.call_action('rune', obj, parents)
                self.walk(obj.type, parents + [obj])
            # case ComplexType():
            #     self.call_action('complex_type', obj, parents)
            # case ComplexValue():
            #     self.call_action('complex', obj, parents)
            #     self.walk(obj.type, parents + [obj])
            case FloatType():
                self.call_action('float_type', obj, parents)
            case FloatValue():
                self.call_action('float', obj, parents)
                self.walk(obj.type, parents + [obj])
            case IntType():
                self.call_action('int_type', obj, parents)
            case IntValue():
                self.call_action('int', obj, parents)
                self.walk(obj.type, parents + [obj])
            case RangeType():
                self.call_action('range', obj, parents)
            case RangeValue():
                self.call_action('range_value', obj, parents)
                self.walk(obj.type, parents + [obj])
            case MonoArrayType():
                self.call_action('array_type', obj, parents)
                self.walk(obj.element_type, parents + [obj])
                self.walk(obj.element_count, parents + [obj])
            case ArrayValue():
                self.call_action('array_value', obj)
                self.walk(obj.type, parents + [obj])
            case MonoCArrayType():
                self.call_action('c_array_type', obj, parents)
                self.walk(obj.element_type, parents + [obj])
                self.walk(obj.element_count, parents + [obj])
            case CArrayValue():
                self.call_action('c_array_value', obj, parents)
                self.walk(obj.type, parents + [obj])
            case CBitFieldType():
                self.call_action('c_bit_field_type', obj, parents)
            case CBitFieldValue():
                self.call_action('c_bit_field_value', obj, parents)
                self.walk(obj.type, parents + [obj])
            case MonoStructType():
                self.call_action('struct_type', obj, parents)
            case MonoStructValue():
                self.call_action('struct', obj, parents)
                self.walk(obj.type, parents + [obj])
            case MonoVariantType():
                self.call_action('variant_type', obj, parents)
            case VariantValue():
                self.call_action('variant', obj, parents)
                self.walk(obj.type, parents + [obj])
            case MonoCStructType():
                self.call_action('c_struct_type', obj, parents)
            case CStructValue():
                self.call_action('c_struct', obj, parents)
                self.walk(obj.type, parents + [obj])
            case MonoCUnionType():
                self.call_action('c_union_type', obj, parents)
            case CUnionValue():
                self.call_action('c_union', obj, parents)
                self.walk(obj.type, parents + [obj])
            case MonoStrType():
                self.call_action('str_type', obj, parents)
            case StrValue():
                self.call_action('str', obj, parents)
                self.walk(obj.type, parents + [obj])
            case StringType():
                self.call_action('string_type', obj, parents)
            case StringValue():
                self.call_action('string', obj, parents)
                self.walk(obj.type, parents + [obj])
            case TypeDef():
                self.call_action('type_def', obj, parents)
                self.walk(obj.type, parents + [obj])
            case TypePlaceholder():
                self.call_action('type_placeholder', obj, parents)
            case LetStmt():
                self.call_action('let_stmt', obj, parents)
                self.walk(obj.expr, parents + [obj])
            case AssignStmt():
                self.call_action('assign_stmt', obj, parents)
                self.walk(obj.expr, parents + [obj])
            case BreakStmt():
                self.call_action('break_stmt', obj, parents)
            case ContinueStmt():
                self.call_action('continue_stmt', obj, parents)
            case ReturnStmt():
                self.call_action('return_stmt', obj, parents)
                self.walk(obj.expr, parents + [obj])
            case IfStmt():
                self.call_action('if_stmt', obj, parents)
                self.walk(obj.conditional_expr, parents + [obj])
                self.walk(obj.else_code, parents + [obj])
            case LoopStmt():
                self.call_action('loop_stmt', obj, parents)
                self.walk(obj.code, parents + [obj])
            case WhileStmt():
                self.call_action('while_stmt', obj, parents)
                self.walk(obj.conditional_expr, parents + [obj])
                self.walk(obj.code, parents + [obj])
            case MatchCaseBlock():
                self.call_action('match_case_block', obj, parents)
                self.walk(obj.variant_field_type_lookup_expr)
                self.walk(obj.code, parents + [obj])
            case DefaultBlock():
                self.call_action('match_case_default_block', obj, parents)
                self.walk(obj.code, parents + [obj])
            case MatchBlock():
                self.call_action('match', obj, parents)
                self.walk(obj.variant_expr, parents + [obj])
                for match_case in obj.match_cases:
                    self.walk(match_case, parents + [obj])
                if obj.default_case:
                    self.walk(obj.default_case, parents + [obj])
            case LiteralExpr():
                self.call_action('literal_expr', obj, parents)
            case UnaryExpr():
                self.call_action('unary_expr', obj, parents)
                self.walk(obj.expr, parents + [obj])
            case BinaryExpr():
                self.call_action('binary_expr', obj, parents)
                self.walk(obj.lhs, parents + [obj])
                self.walk(obj.rhs, parents + [obj])
            case AttributeLookupExpr():
                self.call_action('attribute_lookup_expr', obj, parents)
                self.walk(obj.obj, parents + [obj])
            case CallExpr():
                self.call_action('call_expr', obj, parents)
                self.walk(obj.function, parents + [obj])
                for arg in obj.arguments:
                    self.walk(arg, parents + [obj])
            case BoolExpr():
                self.call_action('bool_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case RuneExpr():
                self.call_action('rune_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            # case ComplexExpr():
            #     self.call_action('complex_expr', obj, parents)
            #     self.walk(obj.type, parents + [obj])
            case FloatExpr():
                self.call_action('float_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case IntExpr():
                self.call_action('int_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case StrExpr():
                self.call_action('str_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case CPtrExpr():
                self.call_action('c_ptr_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case CVoidExpr():
                self.call_action('c_void_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case BoolLiteralExpr():
                self.call_action('bool_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case RuneLiteralExpr():
                self.call_action('rune_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            # case ComplexLiteralExpr():
            #     self.call_action('complex_literal_expr', obj, parents)
            #     self.walk(obj.type, parents + [obj])
            case FloatLiteralExpr():
                self.call_action('float_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case IntLiteralExpr():
                self.call_action('int_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
            case StrLiteralExpr():
                self.call_action('str_literal_expr', obj, parents)
                self.walk(obj.type, parents + [obj])
