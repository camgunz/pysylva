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

    def __init__(self, location, fields):
        SylvaParamType.__init__(self, location)
        self.fields = fields

    # pylint: disable=arguments-differ
    def add_monomorphization(self, location, name, module, fields):
        if len(self.fields) != len(fields):
            raise errors.InvalidParameterization(
                location, 'Mismatched number of fields'
            )

        for sf, f in zip(self.fields, fields):
            if sf.type is None:
                continue
            if sf.type != f.type:
                raise errors.InvalidParameterization(
                    f.location, 'Mismatched field type'
                )

        mvt = MonoVariantType(location, name, module)
        mvt.set_fields(fields)
        return SylvaParamType.add_monomorphization(self, mvt)


class Variant(Union):
    pass
