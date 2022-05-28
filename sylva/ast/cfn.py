from functools import cached_property

from llvmlite import ir

from .. import errors, utils
from .defs import TypeDef
from .sylva_type import SylvaType


class BaseCFnType(SylvaType):

    def __init__(self, location, parameters, return_type):
        SylvaType.__init__(self, location)

        dupes = utils.get_dupes(p.name for p in parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

        self.parameters = parameters
        self.return_type = return_type

        params = []

        for p in self.parameters:
            params.append(p.type.llvm_type)

        self.llvm_type = ir.FunctionType(
            self.return_type.llvm_type if self.return_type else ir.VoidType(),
            params
        )

    def __eq__(self, other):
        return ( # yapf: disable
            SylvaType.__eq__(self, other) and
            len(self.parameters) == len(other.parameters) and
            all(
                p.name == op.name and p.type == op.type
                for p, op in zip(self.parameters, other.parameters)
            ) and
            other.return_type == self.return_type
        )

    @cached_property
    def mname(self):
        return ''.join([
            '3cfn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])


class CFnType(BaseCFnType):
    pass


class CFnPointerType(BaseCFnType):

    def __init__(self, location, parameters, return_type):
        BaseCFnType.__init__(self, location, parameters, return_type)
        self.llvm_type = self.llvm_type.as_pointer()

    @cached_property
    def mname(self):
        return ''.join([
            '4cfnp',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])


class CBlockFnType(BaseCFnType):

    @cached_property
    def mname(self):
        return ''.join([
            '4cbfn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])


class CBlockFnPointerType(BaseCFnType):

    def __init__(self, location, parameters, return_type):
        BaseCFnType.__init__(self, location, parameters, return_type)
        self.llvm_type = self.llvm_type.as_pointer()

    @cached_property
    def mname(self):
        return ''.join([
            '5cbfnp',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])


class CFnDef(TypeDef):

    def llvm_define(self, llvm_module):
        return ir.Function(llvm_module, self.type.llvm_type, self.name)
