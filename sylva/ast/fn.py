from functools import cached_property

from llvmlite import ir

from .. import errors, utils
from .defs import ParamTypeDef
from .sylva_type import SylvaParamType, SylvaType


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
            '2fn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


class FnType(SylvaParamType):

    def get_or_create_monomorphization(
        self, location, parameters, return_type
    ):
        for mm in self.monomorphizations:
            if (mm.return_type == return_type and
                    len(mm.parameters) == len(parameters) and
                    all(p.type == mmp.type for p,
                        mmp in zip(parameters, mm.parameters))):
                return mm

        mm = MonoFnType(location, parameters, return_type)

        self.add_monomorphization(mm)

        return mm


class Fn(ParamTypeDef):

    def __init__(self, location, name, type, code):
        ParamTypeDef.__init__(self, location, name, type)
        self.code = code

    def emit(self, obj, module, builder, scope, name):
        llvm_module = module.type.llvm_type
        llvm_func_type = self.type.emit(llvm_module)
        llvm_func = ir.Function(llvm_module, llvm_func_type, name=self.name)
        block = llvm_func.append_basic_block()
        builder = ir.IRBuilder(block=block)
        scope = {}
        for arg, param in zip(llvm_func_type.args, self.type.parameters):
            param.emit(arg, None, builder, scope)
        for node in self.code:
            node.emit(self, llvm_module, builder, scope)
