import typing

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors, utils
from .defs import Def
from .expr import Expr, ValueExpr
from .statement import Stmt
from .sylva_type import LLVMTypeMixIn, ParamTypeMixIn, SylvaType
from .type_mapping import Parameter


@define(eq=False, slots=True)
class MonoFunctionType(SylvaType, LLVMTypeMixIn):
    parameters: typing.List[Parameter] = field()
    return_type: SylvaType
    llvm_value: None | ir.Function = None
    implementations: typing.List = []

    # pylint: disable=unused-argument
    @parameters.validator
    def check_parameters(self, attribute, parameters):
        dupes = utils.get_dupes(p.name for p in parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

    def mangle(self):
        # pylint: disable=not-an-iterable
        params = ''.join(p.type.mangle() for p in self.parameters)
        base = f'fn{params}{self.return_type.mangle()}'
        return f'{len(base)}{base}'

    def get_llvm_type(self, module):
        return ir.FunctionType( # yapf: disable
            (
                self.return_type.get_llvm_type(module)
                if self.return_type else ir.VoidType()
            ),
            # pylint: disable=not-an-iterable
            [p.type.get_llvm_type(module) for p in self.parameters]
        )


@define(eq=False, slots=True)
class FunctionType(SylvaType, ParamTypeMixIn):
    monomorphizations: typing.List[MonoFunctionType] = []

    @classmethod
    def Def(cls, location, parameters, return_type):
        return cls(
            location=location,
            monomorphizations=[
                MonoFunctionType(location, parameters, return_type)
            ]
        )

    def add_monomorphization(self, mono_function_type):
        index = len(self.monomorphizations)
        self.monomorphizations.append(mono_function_type)
        return index


@define(eq=False, slots=True)
class FunctionExpr(ValueExpr):
    type: FunctionType


@define(eq=False, slots=True)
class FunctionDef(Def):
    type: FunctionType
    code: typing.List[Expr | Stmt]

    def get_llvm_value(self, index):
        return self.type.monomorphizations[index].llvm_value

    def set_llvm_value(self, index, llvm_value):
        self.type.monomorphizations[index].llvm_value = llvm_value
