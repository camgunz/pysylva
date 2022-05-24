from attrs import define, field


@define(eq=False, slots=True)
class Node:
    location = field()


@define(eq=False, slots=True)
class Decl(Node):
    name = field()
