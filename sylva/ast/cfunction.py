import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors, utils
from .defs import Def
from .sylva_type import LLVMTypeMixIn, SylvaType
from .type_mapping import Parameter


@define(eq=False, slots=True)
class BaseCFunctionType(SylvaType, LLVMTypeMixIn):
    parameters: typing.List[Parameter] = field()
    return_type: SylvaType
    implementations: typing.List = []

    # pylint: disable=unused-argument
    @parameters.validator
    def check_parameters(self, attribute, parameters):
        dupes = utils.get_dupes(p.name for p in parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

    def get_llvm_type(self, module):
        params = []

        for p in self.parameters:
            params.append(p.type.get_llvm_type(module))

        return ir.FunctionType(
            self.return_type.get_llvm_type(module)
            if self.return_type else ir.VoidType(),
            params
        )


@define(eq=False, slots=True)
class CFunctionType(BaseCFunctionType):
    pass


@define(eq=False, slots=True)
class CFunctionPointerType(BaseCFunctionType):

    def get_llvm_type(self, module):
        return super().get_llvm_type(module).as_pointer()


@define(eq=False, slots=True)
class CBlockFunctionType(BaseCFunctionType):
    pass


@define(eq=False, slots=True)
class CBlockFunctionPointerType(BaseCFunctionType):

    def get_llvm_type(self, module):
        return super().get_llvm_type(module).as_pointer()


@define(eq=False, slots=True)
class CFunctionDef(Def):
    type: CFunctionType
    llvm_value: None | ir.Function = None
