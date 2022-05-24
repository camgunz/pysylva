import typing

from functools import cached_property

from attrs import define
from llvmlite import ir # type: ignore

from .. import utils
from .array import MonoArrayType
from .defs import TypeDef


@define(eq=False, slots=True)
class CArrayType(MonoArrayType):
    # [TODO] I think these... are also now Param?
    element_count: int
    implementations: typing.List = []

    @cached_property
    def mname(self):
        return ''.join([
            '2ca',
            self.element_type.mname,
            utils.len_prefix(str(self.element_count))
        ])
