import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors, utils
from .defs import Def
from .sylva_type import SylvaType
from .type_mapping import Parameter


@define(eq=False, slots=True)
class BaseCFunctionType(SylvaType):
    implementations: typing.List = []
    llvm_type = field(init=False)
    parameters: typing.List[Parameter] = field(default=[])
    return_type: SylvaType

    # pylint: disable=unused-argument
    @parameters.validator
    def check_parameters(self, attribute, parameters):
        dupes = utils.get_dupes(p.name for p in parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

    @llvm_type.default
    def _llvm_type_factory(self):
        params = []

        for p in self.parameters:
            params.append(p.type.llvm_type)

        return ir.FunctionType(
            self.return_type.llvm_type if self.return_type else ir.VoidType(),
            params
        )


@define(eq=False, slots=True)
class CFunctionType(BaseCFunctionType):
    pass


@define(eq=False, slots=True)
class CFunctionPointerType(BaseCFunctionType):
    llvm_type = field(init=False)

    @llvm_type.default
    def _llvm_type_factory(self):
        params = []

        # pylint: disable=not-an-iterable
        for p in self.parameters:
            params.append(p.type.llvm_type)

        return ir.FunctionType(
            self.return_type.llvm_type if self.return_type else ir.VoidType(),
            params
        ).as_pointer()


@define(eq=False, slots=True)
class CBlockFunctionType(BaseCFunctionType):
    pass


@define(eq=False, slots=True)
class CBlockFunctionPointerType(BaseCFunctionType):
    llvm_type = field(init=False)

    @llvm_type.default
    def _llvm_type_factory(self):
        params = []

        # pylint: disable=not-an-iterable
        for p in self.parameters:
            params.append(p.type.llvm_type)

        return ir.FunctionType(
            self.return_type.llvm_type if self.return_type else ir.VoidType(),
            params
        ).as_pointer()


@define(eq=False, slots=True)
class CFunctionDef(Def):
    type: CFunctionType
    llvm_value: None | ir.Function = None
