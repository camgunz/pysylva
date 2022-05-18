from attrs import define
from llvmlite import ir # type: ignore

from .. import errors
from .defs import Def, LLVMDefMixIn
from .operator import AttributeLookupMixIn
from .pointer import GetElementPointerExpr
from .struct import BaseStructType


@define(eq=False, slots=True)
class CStructType(BaseStructType):
    pass


@define(eq=False, slots=True)
class CStructDef(Def, LLVMDefMixIn, AttributeLookupMixIn):
    llvm_value: None | ir.Value = None

    def get_attribute(self, location, name):
        f = self.type.get_attribute(location, name)
        if not f:
            raise errors.NoSuchField(location, name)
        return f

    def lookup_attribute(self, location, name, module):
        f = self.get_attribute(location, name)
        if not f:
            raise errors.NoSuchField(location, name)
        return GetElementPointerExpr(
            location, type=f.type, obj=self, index=f.index, name=name
        )

    def get_slot(self, location, index):
        if index >= len(self.type.fields):
            raise errors.IndexOutOfBounds(location)
        return self.type.fields[index]

    def index_slot(self, location, index):
        return self.get_slot(location, index).get_value_expr(location=location)
