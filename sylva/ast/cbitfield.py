from functools import cached_property

from llvmlite import ir

from .. import utils
from .sylva_type import SylvaType


class CBitFieldType(SylvaType):

    def __init__(self, location, bits, signed, field_size):
        SylvaType.__init__(self, location)
        self.llvm_type = ir.IntType(bits)
        self.bits = bits
        self.signed = signed
        self.field_size = field_size

    @cached_property
    def mname(self):
        return utils.mangle(['cbf', self.bits, self.signed, self.field_size])
