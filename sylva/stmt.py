from dataclasses import dataclass, field
from typing import Optional

from sylva.builtins import CodeBlock, SylvaObject
from sylva.expr import BoolExpr, Expr, VariantFieldTypeLookupExpr
from sylva.location import Location


@dataclass(kw_only=True)
class Stmt(SylvaObject):
    location: Location


@dataclass(kw_only=True)
class StmtBlock(Stmt):
    code: CodeBlock


@dataclass(kw_only=True)
class LetStmt(Stmt):
    name: str
    expr: Expr


@dataclass(kw_only=True)
class AssignStmt(Stmt):
    name: str
    expr: Expr


@dataclass(kw_only=True)
class BreakStmt(Stmt):
    pass


@dataclass(kw_only=True)
class ContinueStmt(Stmt):
    pass


@dataclass(kw_only=True)
class ReturnStmt(Stmt):
    expr: Expr


@dataclass(kw_only=True)
class IfBlock(StmtBlock):
    conditional_expr: BoolExpr
    else_code: CodeBlock


@dataclass(kw_only=True)
class LoopBlock(StmtBlock):
    code: CodeBlock


@dataclass(kw_only=True)
class WhileBlock(StmtBlock):
    conditional_expr: BoolExpr
    code: CodeBlock


@dataclass(kw_only=True)
class MatchCaseBlock(StmtBlock):
    variant_name: str
    variant_field_type_lookup_expr: VariantFieldTypeLookupExpr
    code: CodeBlock


@dataclass(kw_only=True)
class DefaultBlock(StmtBlock):
    code: CodeBlock


@dataclass(kw_only=True)
class MatchBlock(Stmt):
    variant_expr: Expr  # [TODO] Make VariantExpr once it exists
    match_cases: list[MatchCaseBlock] = field(default_factory=list)
    default_case: Optional[DefaultBlock] = None
