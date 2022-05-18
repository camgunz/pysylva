from attrs import define

from .base import Node


@define(eq=False, slots=True)
class Decl(Node):
    name: str
