from functools import cached_property

from attrs import define, field

from .. import errors, utils
from .attribute_lookup import AttributeLookupMixIn
from .defs import SelfReferentialParamTypeDef
from .pointer import GetElementPointerExpr
from .sylva_type import SylvaParamType, SylvaType


@define(eq=False, slots=True)
class BaseStructType(SylvaType, AttributeLookupMixIn):
    fields = field()

    # self._size = 0
    # self._alignment = 1
    # self._offsets = {}
    # for name, type in self.fields:
    #     self._size = utils.round_up_to_multiple(
    #       self._size, type.alignment
    #     )
    #     self._alignment = max(self._alignment, type.alignment)
    #     self._offsets[name] = self._size
    #     self._size += type.size
    # self._size = utils.round_up_to_multiple(self._size, self._alignment)

    @fields.validator
    def check_fields(self, attribute, fields):
        dupes = utils.get_dupes(f.name for f in fields)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

    @cached_property
    def mname(self):
        return ''.join(['6struct', ''.join(f.type.mname for f in self.fields)])

    def get_attribute(self, location, name):
        # [TODO] These are reflection attributes, but since we're inside the
        #        type, they're really plain old attributes.
        raise NotImplementedError()

    def emit_attribute_lookup(self, location, module, builder, scope, name):
        # [TODO] These are reflection attributes, but since we're inside the
        #        type, they're really plain old attributes.
        raise NotImplementedError()


@define(eq=False, slots=True)
class MonoStructType(BaseStructType):
    pass


@define(eq=False, slots=True)
class StructType(SylvaParamType):
    pass


@define(eq=False, slots=True)
class StructDef(SelfReferentialParamTypeDef, AttributeLookupMixIn):

    def get_attribute(self, location, name):
        f = self.type.get_attribute(location, name)
        if not f:
            raise errors.NoSuchField(location, name)
        return f

    def emit_attribute_lookup(self, location, module, builder, scope, name):
        f = self.get_attribute(location, name)
        if f is not None:
            return GetElementPointerExpr(
                location, type=f.type, obj=self, index=f.index, name=name
            )
        return super().emit_attribute_lookup(
            location, module, builder, scope, name
        )

    def llvm_define(self, llvm_module):
        pass
