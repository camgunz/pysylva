from functools import cached_property

from .. import errors, utils
from ..location import Location
from .sylva_type import SylvaParamType, SylvaType
from .value import Value


class BaseStructType(SylvaType):

    def __init__(self, location, fields):
        dupes = utils.get_dupes(f.name for f in fields)
        if dupes:
            raise errors.DuplicateFields(self, dupes)
        SylvaType.__init__(self, location)
        self.fields = fields

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

    @cached_property
    def mname(self):
        return ''.join(['6struct', ''.join(f.type.mname for f in self.fields)])

    def get_attribute(self, name):
        # [TODO] These are reflection attributes, but since we're inside the
        #        type, they're really plain old attributes.
        raise NotImplementedError()

    def emit_attribute_lookup(self, module, builder, scope, name):
        # [TODO] These are reflection attributes, but since we're inside the
        #        type, they're really plain old attributes.
        raise NotImplementedError()


class MonoStructType(BaseStructType):

    def __eq__(self, other):
        return (
            SylvaType.__eq__(self, other) and
            len(self.fields) == len(other.fields) and
            all(f.type == of.type for f, of in zip(self.fields, other.fields))
        )


class StructType(SylvaParamType):

    def get_or_create_monomorphization(self, fields):
        for mm in self.monomorphizations:
            if (len(fields) == len(mm.fields) and all(
                    f.type == mmf.type for f, mmf in zip(fields, mm.fields))):
                return mm
            return mm

        mm = MonoStructType(Location.Generate(), fields)

        self.add_monomorphization(mm)

        return mm


class Struct(Value):

    def get_attribute(self, name):
        for f in self.type.fields:
            if f.name == name:
                return f
        return Value.get_attribute(self, name)

    def emit_attribute_lookup(self, module, builder, scope, name):
        f = self.get_attribute(name)
        if f is not None:
            return f.emit(self, module, builder, scope, name)
        return super().emit_attribute_lookup(module, builder, scope, name)
