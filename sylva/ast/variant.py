from functools import cached_property

from llvmlite import ir

from .. import errors, utils
from .sylva_type import SylvaParamType
from .union import BaseUnionType, Union


class MonoVariantType(BaseUnionType):

    @cached_property
    def mname(self):
        return ''.join([
            '7variant', ''.join(f.type.mname for f in self.fields)
        ])

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
            self.llvm_type.set_body(
                largest_field.type.llvm_type,
                ir.IntType(utils.round_up_to_multiple(len(fields), 8))
            )
        else:
            self.llvm_type = ir.LiteralStructType([
                largest_field.type.llvm_type,
                ir.IntType(utils.round_up_to_multiple(len(fields), 8))
            ])

        self.fields = fields


class VariantType(SylvaParamType):

    def get_or_create_monomorphization(self, location, name, module, fields):
        for mm in self.monomorphizations:
            if (len(fields) == len(mm.fields) and all(
                    f.type == mmf.type for f, mmf in zip(fields, mm.fields))):
                return mm

        mm = MonoVariantType(location, name, module)
        mm.set_fields(fields)

        self.add_monomorphization(mm)

        return mm


class Variant(Union):
    pass
