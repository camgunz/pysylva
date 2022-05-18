from attrs import define, field

from .base import Node
from .sylva_type import SylvaParamType, SylvaType


@define(eq=False, slots=True)
class BaseDef(Node):
    name: str
    type = field()


@define(eq=False, slots=True)
class Def(BaseDef):
    type: SylvaType


@define(eq=False, slots=True)
class ParamDef(BaseDef):
    type: SylvaParamType
