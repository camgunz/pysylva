from llvmlite import ir

from .. import errors, utils
from .struct import MonoStructType
from .sylva_type import SylvaType
from .value import Value


class BaseUnionType(MonoStructType):

    def __eq__(self, other):
        return (
            SylvaType.__eq__(self, other) and
            len(self.fields) == len(other.fields) and
            all(f.type == of.type for f, of in zip(self.fields, other.fields))
        )

    def set_fields(self, fields):
        dupes = utils.get_dupes(f.name for f in fields)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

        llvm_fields = []
        largest_field = None

        for f in fields:
            llvm_fields.append(f.type.llvm_type)
            if largest_field is None or f.type.get_size(
            ) > largest_field.type.get_size():
                largest_field = f

        if self.name:
            self.llvm_type.set_body(largest_field.type.llvm_type)
        else:
            self.llvm_type = ir.LiteralStructType([
                largest_field.type.llvm_type
            ])

        self.fields = fields


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
