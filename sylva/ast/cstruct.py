from functools import cached_property

from .. import errors
from .attribute_lookup import AttributeLookupMixIn
from .defs import SelfReferentialTypeDef
from .struct import BaseStructType


class CStructType(BaseStructType):

    @cached_property
    def mname(self):
        return ''.join([
            '7cstruct', ''.join(f.type.mname for f in self.fields)
        ])


class CStructDef(SelfReferentialTypeDef, AttributeLookupMixIn):

    def get_attribute(self, name):
        f = self.type.get_attribute(name)
        if not f:
            raise errors.NoSuchField(self.location, name)
        return f

    def emit_attribute_lookup(self, module, builder, scope, name):
        f = self.get_attribute(name)
        if f is not None:
            return f.emit(self, module, builder, scope, name)
        return super().emit_attribute_lookup(module, builder, scope, name)
