from dataclasses import dataclass, field
from functools import cached_property

from .dynarray import MonoDynarrayType


@dataclass(kw_only=True)
class StringType(MonoDynarrayType):
    name: str = field(init=False, default='string')

    def __init__(self, location=None):
        from .type_singleton import TypeSingletons

        MonoDynarrayType.__init__(
            self, location=location, element_type=TypeSingletons.U8
        )

    @cached_property
    def mname(self):
        return 'string'
