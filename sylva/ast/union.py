from .. import errors, utils
from .sylva_type import SylvaType
from .value import Value


class BaseUnionType(SylvaType):

    def __init__(self, location, fields):
        SylvaType.__init__(self, location)

        dupes = utils.get_dupes(f.name for f in fields)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

        self.fields = fields

    def __eq__(self, other):
        return (
            SylvaType.__eq__(self, other) and
            len(self.fields) == len(other.fields) and
            all(f.type == of.type for f, of in zip(self.fields, other.fields))
        )

    def get_largest_field(self):
        largest_field = self.fields[0]
        for f in self.fields[1:]:
            if f.get_size() > largest_field.get_size():
                largest_field = f
        return largest_field.llvm_type

    def get_attribute(self, name):
        for f in self.fields:
            if f.name == name:
                return f


class Union(Value):

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
