from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional

from sylva import errors, utils
from sylva.const import ConstExpr, ConstTypeExpr
from sylva.sylva_type import SylvaType
from sylva.parameter import ParameterExpr


@dataclass(kw_only=True)
class CFnPointerType(BaseCFnType):

    @cached_property
    def mname(self):
        return ''.join([
            '4cfnp',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


@dataclass(kw_only=True)
class CBlockFnType(BaseCFnType):

    @cached_property
    def mname(self):
        return ''.join([
            '4cbfn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


@dataclass(kw_only=True)
class CBlockFnPointerType(BaseCFnType):

    @cached_property
    def mname(self):
        return ''.join([
            '5cbfnp',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


@dataclass(kw_only=True)
class CFnExpr(ConstExpr):
    type: BaseCFnType

    @cached_property
    def mname(self):
        return self.name
