from dataclasses import dataclass
from functools import cached_property

from .struct import BaseStructType


@dataclass(kw_only=True)
class CStructType(BaseStructType):

    @cached_property
    def mname(self):
        return 'cstruct'
