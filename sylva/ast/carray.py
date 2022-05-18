import typing

from attrs import define

from .array import MonoArrayType
from .defs import Def, LLVMDefMixIn


@define(eq=False, slots=True)
class CArrayType(MonoArrayType):
    # [TODO] I think these... are also now Param?
    element_count: int
    implementations: typing.List = []


@define(eq=False, slots=True)
class CArrayDef(Def, LLVMDefMixIn):
    pass
