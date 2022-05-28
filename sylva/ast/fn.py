from functools import cached_property

from llvmlite import ir

from .. import errors, utils
from .defs import ParamTypeDef
from .sylva_type import SylvaParamType, SylvaType
from .value import Value, ValueExpr


class MonoFnType(SylvaType):

    def __init__(self, location, parameters, return_type):
        SylvaType.__init__(self, location)

        dupes = utils.get_dupes(p.name for p in parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

        self.parameters = parameters
        self.return_type = return_type
        self.llvm_type = ir.FunctionType( # yapf: disable
            (
                self.return_type.llvm_type
                if self.return_type else ir.VoidType()
            ),
            [p.type.llvm_type for p in self.parameters]
        )

    @cached_property
    def mname(self):
        return ''.join([
            '2fn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname
        ])


class FnType(SylvaParamType):
    pass


class FnExpr(ValueExpr):
    pass


class FnDef(ParamTypeDef):

    def __init__(self, location, name, type, code):
        ParamTypeDef.__init__(self, location, name, type)
        self.code = code

    def llvm_define(self, llvm_module):
        llvm_func_type = self.type.emit(llvm_module)
        llvm_func = ir.Function(llvm_module, llvm_func_type, name=self.name)
        block = llvm_func.append_basic_block()
        builder = ir.IRBuilder(block=block)
        scope = {}
        for arg, param in zip(llvm_func_type.args, self.type.parameters):
            value = Value(
                location=param.location,
                name=param.name,
                ptr=arg,
                type=param.type
            )
            builder.store(value.ptr, param.emit())
            scope[param.name] = value
        for node in self.code:
            node.emit(llvm_module, builder, scope)
