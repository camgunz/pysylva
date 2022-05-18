from attrs import define

from .decl import Decl


@define(eq=False, slots=True)
class RequirementDecl(Decl):
    pass
