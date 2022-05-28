from functools import cached_property

from .struct import BaseStructType


class CStructType(BaseStructType):

    @cached_property
    def mname(self):
        return ''.join([
            '7cstruct', ''.join(f.type.mname for f in self.fields)
        ])
