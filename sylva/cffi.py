from enum import Enum

import llvmlite

class CAtomicType:

    __slots__ = ('size', 'alignment')

    def __init__(self, size, alignment):
        self.size = size
        self.alignment = alignment

class CAtomicTypes(Enum):
    Integer = CAtomicType()
    # Int
    # Float/Double
    # Void

