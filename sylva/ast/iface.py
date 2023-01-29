from dataclasses import dataclass
from functools import cached_property
from typing import Union

from sylva import errors, utils
from sylva.ast.fn import FnType, Fn
from sylva.ast.sylva_type import SylvaType


@dataclass(kw_only=True)
class IfaceType(SylvaType):
    functions: dict[str, Union[FnType, Fn]]

    def __post_init__(self):
        dupes = utils.get_dupes(self.functions.keys())
        if dupes:
            raise errors.DuplicateFields(self, dupes)

    def get_attribute(self, name):
        return self.functions.get(name)

    @cached_property
    def mname(self):
        function_mnames = sorted([f.mname for f in self.functions.values()])
        return ''.join(['if', ''.join(function_mnames)])
