from dataclasses import dataclass
from functools import cached_property

from sylva.ast.union import UnionType


@dataclass(kw_only=True)
class CUnionType(UnionType):

    @cached_property
    def mname(self):
        return ''.join(['6cunion', ''.join(f.type.mname for f in self.fields)])
