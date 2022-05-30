from functools import cached_property

from .defs import TypeDef
from .struct import BaseStructType


class CStructType(BaseStructType):

    @cached_property
    def mname(self):
        return 'cstruct'


class CStructTypeDef(TypeDef):

    def __init__(self, type):
        TypeDef.__init__(self, type.location, type.name, type=type)

    @cached_property
    def mname(self):
        return self.name
