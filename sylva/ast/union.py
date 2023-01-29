from dataclasses import dataclass

from sylva.ast.struct import MonoStructType


@dataclass(kw_only=True)
class UnionType(MonoStructType):
    pass

    # def set_fields(self, fields):
    #     dupes = utils.get_dupes(f.name for f in fields)
    #     if dupes:
    #         raise errors.DuplicateFields(self, dupes)

    #     llvm_fields = []
    #     largest_field = None

    #     for f in fields:
    #         llvm_fields.append(f.type.llvm_type)
    #         if largest_field is None or f.type.get_size(
    #         ) > largest_field.type.get_size():
    #             largest_field = f

    #     if self.name:
    #         self.llvm_type.set_body(largest_field.type.llvm_type)
    #     else:
    #         self.llvm_type = ir.LiteralStructType([
    #             largest_field.type.llvm_type
    #         ])

    #     self.fields = fields
