from functools import cached_property

from attrs import define, field
from llvmlite import ir

from .. import errors, utils
from .defs import TypeDef
from .sylva_type import SylvaType


@define(eq=False, slots=True)
class BaseCFnType(SylvaType):
    parameters = field(default=[])
    return_type = field()

    @parameters.validator
    def check_parameters(self, attribute, parameters):
        dupes = utils.get_dupes(p.name for p in parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        params = []

        for p in self.parameters:
            params.append(p.type.llvm_type)

        return ir.FunctionType(
            self.return_type.llvm_type if self.return_type else ir.VoidType(),
            params
        )

    @cached_property
    def mname(self):
        return ''.join([
            '3cfn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])


@define(eq=False, slots=True)
class CFnType(BaseCFnType):
    pass


@define(eq=False, slots=True)
class CFnPointerType(BaseCFnType):

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        params = []

        for p in self.parameters:
            params.append(p.type.llvm_type)

        return ir.FunctionType(
            self.return_type.llvm_type if self.return_type else ir.VoidType(),
            params
        ).as_pointer()

    @cached_property
    def mname(self):
        return ''.join([
            '4cfnp',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])


@define(eq=False, slots=True)
class CBlockFnType(BaseCFnType):

    @cached_property
    def mname(self):
        return ''.join([
            '4cbfn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])


@define(eq=False, slots=True)
class CBlockFnPointerType(BaseCFnType):

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        params = []

        for p in self.parameters:
            params.append(p.type.llvm_type)

        return ir.FunctionType(
            self.return_type.llvm_type if self.return_type else ir.VoidType(),
            params
        ).as_pointer()

    @cached_property
    def mname(self):
        return ''.join([
            '5cbfnp',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])


@define(eq=False, slots=True)
class CFnDef(TypeDef):

    def llvm_define(self, llvm_module):
        return ir.Function(llvm_module, self.type.llvm_type, self.name)
