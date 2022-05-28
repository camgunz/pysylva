from functools import cached_property

from .pointer import BasePointerExpr, BasePointerType


class CPtrType(BasePointerType):

    def __init__(
        self, location, referenced_type, referenced_type_is_exclusive
    ):
        BasePointerType.__init__(
            self, location, referenced_type, is_exclusive=False
        )
        self.referenced_type_is_exclusive = referenced_type_is_exclusive

    @cached_property
    def mname(self):
        return ''.join([
            '2cp',
            self.referenced_type.mname,
        ])


class CPtrExpr(BasePointerExpr):

    def __init__(self, location, type, expr):
        BasePointerExpr.__init__(self, location, type)
        self.expr = expr
