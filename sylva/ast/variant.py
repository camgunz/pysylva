from dataclasses import dataclass, field
from functools import cached_property
from typing import Union

from sylva.ast.struct import StructType
from sylva.ast.union import UnionType
from sylva.ast.sylva_type import SylvaType, TypeParam


@dataclass(kw_only=True)
class MonoVariantType(UnionType):
    fields: dict[str, SylvaType] = field(default_factory=dict)

    @cached_property
    def mname(self):
        return ''.join([
            '7variant', ''.join(f.type.mname for f in self.fields)
        ])

    # def set_fields(self, fields):
    #     dupes = utils.get_dupes(f.name for f in fields)
    #     if dupes:
    #         raise errors.DuplicateFields(self, dupes)

    #     llvm_fields = []
    #     largest_field = None

    #     seen = set()
    #     self.type_parameters = []

    #     for f in fields:
    #         llvm_fields.append(f.type.llvm_type)

    #         self._type_parameters.extend([
    #             tp for tp in f.type_parameters
    #             if tp.name not in seen and not seen.add(tp.name)
    #         ])

    #         if largest_field is None:
    #             largest_field = f
    #             continue

    #         if f.type.get_size() > largest_field.type.get_size():
    #             largest_field = f

    #     if self.name:
    #         self.llvm_type.set_body(
    #             largest_field.type.llvm_type,
    #             ir.IntType(utils.round_up_to_power_of_two(len(fields)))
    #         )
    #     else:
    #         self.llvm_type = ir.LiteralStructType([
    #             largest_field.type.llvm_type,
    #             ir.IntType(utils.round_up_to_power_of_two(len(fields)))
    #         ])

    #     self.fields = fields


class VariantType(StructType):
    fields: dict[str, SylvaType] = field(default_factory=dict) # type: ignore
    _type_parameters: list[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        seen = set()
        self._type_parameters = []
        for field in self.fields.values():
            self._type_parameters.extend([
                tp for tp in field.type_parameters
                if tp.name not in seen and not seen.add(tp.name)
            ])

    def parameterize(self, location, params):
        # Result(u32)
        # params = [
        fields = self.get_parameterized_types(location, self.fields, params)

        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(self.name, fields):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoVariantType(
            location=location, name=self.name, module=self.module
        )
        # [FIXME] Normally we have access to the type when building fields,
        #         meaning that building self-referential fields is easy. But
        #         here we've wrapped that all up in this method, so it's
        #         currently not possible to create a struct monomorphization
        #         with a self-referential field. I think the fix here is
        #         something like a `SelfReferentialField`, probably.
        mm.set_fields(fields)
        self.monomorphizations.append(mm)

        return index, mm

    # pylint: disable=arguments-differ
    def get_or_create_monomorphization(self, location, exprs):
        fields = self.get_parameterized_types_from_expressions(
            location, self.fields, exprs
        )

        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(self.name, fields):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoVariantType(
            location=location, name=self.name, module=self.module
        )
        # [FIXME] Normally we have access to the type when building fields,
        #         meaning that building self-referential fields is easy. But
        #         here we've wrapped that all up in this method, so it's
        #         currently not possible to create a struct monomorphization
        #         with a self-referential field. I think the fix here is
        #         something like a `SelfReferentialField`, probably.
        mm.set_fields(fields)
        self.monomorphizations.append(mm)

        return index, mm


class Variant(UnionType):
    pass
