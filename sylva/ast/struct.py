import typing

from functools import cached_property

from attrs import define, field

from .. import errors, utils
from .attribute_lookup import AttributeLookupMixIn
from .defs import SelfReferentialParamTypeDef
from .pointer import GetElementPointerExpr
from .sylva_type import SylvaParamType, SylvaType
from .type_mapping import Field


@define(eq=False, slots=True)
class BaseStructType(SylvaType, AttributeLookupMixIn):
    name: str | None
    fields: typing.List[Field] = field()
    implementations: typing.List = []

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

    # pylint: disable=unused-argument
    @fields.validator
    def check_fields(self, attribute, fields):
        dupes = utils.get_dupes(f.name for f in fields)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

    @cached_property
    def mname(self):
        # pylint: disable=not-an-iterable
        return ''.join(['6struct', ''.join(f.type.mname for f in self.fields)])

    # pylint: disable=unused-argument
    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f


@define(eq=False, slots=True)
class MonoStructType(BaseStructType):
    pass


@define(eq=False, slots=True)
class StructType(SylvaParamType):
    monomorphizations: typing.List[MonoStructType] = []
    implementations: typing.List = []


@define(eq=False, slots=True)
class StructDef(SelfReferentialParamTypeDef, AttributeLookupMixIn):

    def get_attribute(self, location, name):
        f = self.type.get_attribute(location, name)
        if not f:
            raise errors.NoSuchField(location, name)
        return f

    # pylint: disable=unused-argument
    def lookup_attribute(self, location, name):
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

    def llvm_define(self, llvm_module):
        pass
