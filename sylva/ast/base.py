from attrs import frozen, field
from sylva.location import Location


@frozen
class Node:
    location: Location = field(kw_only=True, factory=Location.Generate)


@frozen
class Decl(Node):
    name: str
