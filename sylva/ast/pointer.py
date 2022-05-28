from functools import cached_property

from llvmlite import ir

from .. import errors
from .attribute_lookup import AttributeLookupMixIn
from .sylva_type import SylvaType
from .value import ValueExpr


class BasePointerType(SylvaType, AttributeLookupMixIn):

    def __init__(self, location, referenced_type, is_exclusive):
        SylvaType.__init__(self, location)
        AttributeLookupMixIn.__init__(self, location)
        self.llvm_type = ir.PointerType(referenced_type.llvm_type)
        self.referenced_type = referenced_type
        self.is_exclusive = is_exclusive

    def get_attribute(self, location, name):
        if not isinstance(self.referenced_type, AttributeLookupMixIn):
            raise errors.ImpossibleLookup(location)
        return self.referenced_type.get_attribute(location, name)


class ReferencePointerType(BasePointerType):

    def __init__(self, location, referenced_type):
        BasePointerType.__init__(
            self, location, referenced_type, is_exclusive=False
        )

    @cached_property
    def mname(self):
        return ''.join(['2rp', self.referenced_type.mname])


class ExclusiveReferencePointerType(BasePointerType):

    def __init__(self, location, referenced_type):
        BasePointerType.__init__(
            self, location, referenced_type, is_exclusive=True
        )

    @cached_property
    def mname(self):
        return ''.join(['2xp', self.referenced_type.mname])


class OwnedPointerType(BasePointerType):

    def __init__(self, location, referenced_type):
        BasePointerType.__init__(
            self, location, referenced_type, is_exclusive=True
        )

    @cached_property
    def mname(self):
        return ''.join(['2op', self.referenced_type.mname])


class BasePointerExpr(ValueExpr):

    @property
    def referenced_type(self):
        return self.type.referenced_type

    @property
    def is_exclusive(self):
        return self.type.is_exclusive


class ReferencePointerExpr(BasePointerExpr):

    def __init__(self, location, type, expr):
        BasePointerExpr.__init__(self, location, type)
        self.expr = expr


class OwnedPointerExpr(BasePointerExpr):
    pass


class MovePointerExpr(BasePointerExpr):

    def __init__(self, location, type, expr):
        BasePointerExpr.__init__(self, location, type)
        self.expr = expr
