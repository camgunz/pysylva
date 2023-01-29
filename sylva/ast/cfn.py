from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional

from sylva import errors, utils
from sylva.ast.parameter import Parameter
from sylva.ast.sylva_type import SylvaType
from sylva.ast.value import Value


@dataclass(kw_only=True)
class BaseCFnType(SylvaType):
    parameters: list[Parameter] = field(default_factory=list)
    return_type: Optional[SylvaType] = field(default=None)

    def __post_init__(self):
        dupes = utils.get_dupes(p.name for p in self.parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

    @cached_property
    def mname(self):
        return ''.join([
            '3cfn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


@dataclass(kw_only=True)
class CFnType(BaseCFnType):
    pass


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
class CFn(Value):

    @cached_property
    def mname(self):
        return self.name
