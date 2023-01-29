from dataclasses import dataclass, field
from functools import cached_property
from typing import Union

from sylva.ast.mod import Mod
from sylva.ast.sylva_type import MonoType, ParamType, SylvaType, TypeParam


@dataclass(kw_only=True)
class BaseStructType(MonoType):
    fields: dict[str, SylvaType] = field(default_factory=dict)

    @cached_property
    def mname(self):
        return ''.join(['6struct', ''.join(f.type.mname for f in self.fields)])


@dataclass(kw_only=True)
class MonoStructType(BaseStructType):
    pass


@dataclass(kw_only=True)
class StructType(ParamType):
    module: Mod
    fields: dict[str, Union[SylvaType, TypeParam]] = field(
        default_factory=dict
    ) # yapf: ignore
    _type_parameters: list[str] = field(default_factory=list, init=False)

    def __post_init__(self):
        self._type_parameters = [
            n for n, f in self.fields.items() if isinstance(f, TypeParam)
        ]

    @property
    def type_parameters(self):
        return self._type_parameters

    def parameterize(self, location, params):
        fields = self.get_parameterized_types(location, self.fields, params)

        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(self.name, fields):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoStructType(location=location, name=self.name)
        # [FIXME] Normally we have access to the type when building fields,
        #         meaning that building self-referential fields is easy. But
        #         here we've wrapped that all up in this method, so it's
        #         currently not possible to create a struct monomorphization
        #         with a self-referential field. I think the fix here is
        #         something like a `SelfReferentialField`, probably.
        mm.fields = fields
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

        mm = MonoStructType(location=location, name=self.name)
        # [FIXME] Normally we have access to the type when building fields,
        #         meaning that building self-referential fields is easy. But
        #         here we've wrapped that all up in this method, so it's
        #         currently not possible to create a struct monomorphization
        #         with a self-referential field. I think the fix here is
        #         something like a `SelfReferentialField`, probably.
        mm.fields = fields
        self.monomorphizations.append(mm)

        return index, mm
