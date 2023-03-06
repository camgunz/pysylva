from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional

from sylva import errors, utils
from sylva.code_block import CodeBlock
from sylva.const import ConstExpr, ConstTypeExpr
from sylva.parameter import ParameterExpr
from sylva.sylva_type import MonoType, ParamType, SylvaType
from sylva.value import Value


@dataclass(kw_only=True)
class FnExpr(ConstExpr):
    type: Fn
