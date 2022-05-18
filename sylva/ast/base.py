from attrs import define

from ..location import Location


@define(eq=False, slots=True)
class Node:
    location: Location


@define(eq=False, slots=True)
class Decl(Node):
    name: str
