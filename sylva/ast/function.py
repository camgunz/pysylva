import typing

from functools import cached_property

from attrs import define, field
from llvmlite import ir # type: ignore

from .. import errors, utils
from .defs import ParamTypeDef
from .expr import Expr, ValueExpr
from .statement import Stmt
from .sylva_type import SylvaParamType, SylvaType
from .type_mapping import Parameter


@define(eq=False, slots=True)
class MonoFunctionType(SylvaType):
    parameters: typing.List[Parameter] = field(default=[])
    return_type: SylvaType | None
    implementations: typing.List = []
    llvm_type = field(init=False)

    # pylint: disable=unused-argument
    @parameters.validator
    def check_parameters(self, attribute, parameters):
        dupes = utils.get_dupes(p.name for p in parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

    @cached_property
    def mname(self):
        # pylint: disable=not-an-iterable
        return ''.join([
            '2fn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])

    @llvm_type.default
    def _llvm_type_factory(self):
        return ir.FunctionType( # yapf: disable
            (
                self.return_type.llvm_type
                if self.return_type else ir.VoidType()
            ),
            # pylint: disable=not-an-iterable
            [p.type.llvm_type for p in self.parameters]
        )


@define(eq=False, slots=True)
class FunctionType(SylvaParamType):
    monomorphizations: typing.List[MonoFunctionType] = []


@define(eq=False, slots=True)
class FunctionExpr(ValueExpr):
    type: typing.Any


@define(eq=False, slots=True)
class FunctionDef(ParamTypeDef):
    type: FunctionType
    code: typing.List[Expr | Stmt]

    def llvm_define(self, llvm_module):
        llvm_func_type = self.type.emit(llvm_module)
        llvm_func = ir.Function(llvm_module, llvm_func_type, name=self.name)
        block = llvm_func.append_basic_block()
        builder = ir.IRBuilder(block=block)
        scope = {}
        for arg, param in zip(llvm_func_type.args, self.type.parameters):
            llvm_param = builder.alloca(param.type.llvm_type, name=param.name)
            builder.store(arg, llvm_param)
            scope[param.name] = llvm_param
        for node in self.code:
            node.emit(llvm_module, builder, scope)
