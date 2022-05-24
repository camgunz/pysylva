from functools import cached_property

from attrs import define

from .. import errors
from .attribute_lookup import AttributeLookupMixIn
from .defs import SelfReferentialTypeDef
from .pointer import GetElementPointerExpr
from .struct import BaseStructType


@define(eq=False, slots=True)
class CStructType(BaseStructType):

    @cached_property
    def mname(self):
        # pylint: disable=not-an-iterable
        return ''.join([
            '7cstruct', ''.join(f.type.mname for f in self.fields)
        ])


@define(eq=False, slots=True)
class CStructDef(SelfReferentialTypeDef, AttributeLookupMixIn):

    def get_attribute(self, location, name):
        f = self.type.get_attribute(location, name)
        if not f:
            raise errors.NoSuchField(location, name)
        return f

    def emit_attribute_lookup(self, location, name):
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
