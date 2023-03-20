from dataclasses import dataclass, field

from sylva import errors
from sylva.builtins import (
    FnValue,
    SylvaObject,
    TypePlaceholder,
)
from sylva.mod import Mod
from sylva.scope import Scope
from sylva.stmt import (
    AssignStmt,
    ReturnStmt,
)
from sylva.visitor import Visitor


@dataclass(kw_only=True)
class TypeChecker(Visitor):
    module: Mod | None = field(init=False, default=None)
    funcs: list[FnValue] = field(init=False, default_factory=list)
    scopes: Scope = field(init=False, default_factory=Scope)

    # [TODO]
    # - Default args for structs/variants
    # - Const defs/arrays/structs/variants

    def enter_assign_stmt(
        self,
        assign_stmt: AssignStmt,
        name: str,
        parents: list[SylvaObject | Mod]
    ):
        # [TODO] Handle things like struct field assignment
        var_type = self.lookup(assign_stmt.name)

        if var_type is None:
            raise errors.UndefinedSymbol(
                assign_stmt.location, assign_stmt.name
            )

        if assign_stmt.expr.type != var_type:
            raise errors.MismatchedVariableType(
                assign_stmt.expr.location, assign_stmt.expr.type, var_type
            )

        # [TODO] Ensure expr's type isn't an aggregate value, requiring an
        #        aggregate deep copy
        # [TODO] Ensure var's type isn't an aggregate

    def enter_return_stmt(
        self,
        return_stmt: ReturnStmt,
        name: str,
        parents: list[SylvaObject | Mod]
    ):
        func = self.current_func

        if (isinstance(return_stmt.expr.type, TypePlaceholder) and
                isinstance(func.type.return_type, TypePlaceholder)):
            if return_stmt.expr.type.name != func.type.return_type.name:
                raise errors.MismatchedReturnType(
                    return_stmt.expr.location,
                    return_stmt.expr.type.name,
                    func.type.return_type.name
                )
        elif return_stmt.expr.type != func.type.return_type:
            raise errors.MismatchedReturnType(
                return_stmt.expr.location,
                return_stmt.expr.type,
                func.type.return_type
            )
