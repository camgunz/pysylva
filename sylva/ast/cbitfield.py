from dataclasses import dataclass
from functools import cached_property

from sylva import utils
from sylva.ast.sylva_type import MonoType


@dataclass(kw_only=True)
class CBitFieldType(MonoType):
    bits: int
    signed: bool
    field_size: int

    @cached_property
    def mname(self):
        return utils.mangle(['cbf', self.bits, self.signed, self.field_size])
