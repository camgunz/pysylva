from functools import cached_property

from attrs import define, field
from llvmlite import ir

from .. import errors, utils
from .defs import ParamTypeDef
from .expr import ValueExpr
from .sylva_type import SylvaParamType, SylvaType
from .value import Value


@define(eq=False, slots=True)
class MonoFnType(SylvaType):
    parameters = field(default=[])
    return_type = field(default=None)

    @parameters.validator
    def check_parameters(self, attribute, parameters):
        dupes = utils.get_dupes(p.name for p in parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

    @cached_property
    def mname(self):
        return ''.join([
            '2fn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return ir.FnType( # yapf: disable
            (
                self.return_type.llvm_type
                if self.return_type else ir.VoidType()
            ),
            [p.type.llvm_type for p in self.parameters]
        )


@define(eq=False, slots=True)
class FnType(SylvaParamType):
    pass


@define(eq=False, slots=True)
class FnExpr(ValueExpr):
    pass


@define(eq=False, slots=True)
class FnDef(ParamTypeDef):
    code = field()

    def llvm_define(self, llvm_module):
        llvm_func_type = self.type.emit(llvm_module)
        llvm_func = ir.Function(llvm_module, llvm_func_type, name=self.name)
        block = llvm_func.append_basic_block()
        builder = ir.IRBuilder(block=block)
        scope = {}
        for arg, param in zip(llvm_func_type.args, self.type.parameters):
            value = Value(
                location=param.location,
                ptr=arg,
                name=param.name,
                type=param.type
            )
            builder.store(value.ptr, param.emit())
            scope[param.name] = value
        for node in self.code:
            node.emit(llvm_module, builder, scope)
