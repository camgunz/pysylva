from attrs import define, field

from .base import Node


@define(eq=False, slots=True)
class Implementation(Node):
    interface = field()
    implementing_type = field()
    funcs = field()
