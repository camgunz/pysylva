import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors, utils
from .attribute_lookup import AttributeLookupMixIn
from .defs import SelfReferentialParamDef
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
    name: str | None
    monomorphizations: typing.List[MonoStructType] = []
    implementations: typing.List = []

    @classmethod
    def Def(cls, location, name, fields):
        return cls(
            location=location,
            name=name,
            monomorphizations=[
                MonoStructType(location=location, name=name, field=fields)
            ]
        )

    def add_monomorphization(self, fields):
        index = len(self.monomorphizations)
        mst = MonoStructType(name=self.name, fields=fields)
        self.monomorphizations.append(mst)
        return index


@define(eq=False, slots=True)
class StructDef(SelfReferentialParamDef, AttributeLookupMixIn):
    llvm_value: None | ir.Value = None

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
