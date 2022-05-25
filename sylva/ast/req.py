from attrs import define

from .base import Decl


@define(eq=False, slots=True)
class ReqDecl(Decl):
    pass
