from llvmlite import ir

from . import ast
from . import types


class CodeGen:

    def __init__(self, module):
        self.module = module
        self.llvm_module = ir.Module(name=self.module.name)

    def compile_const(self, const):
        raise NotImplementedError()

    def compile_enum(self, enum):
        raise NotImplementedError()

    def compile_function_type(self, function_type):
        raise NotImplementedError()

    def compile_c_function_type(self, c_function_type):
        raise NotImplementedError()

    def compile_c_block_function_type(self, c_block_function_type):
        raise NotImplementedError()

    def compile_function(self, function):
        raise NotImplementedError()

    def compile_c_function(self, c_function):
        raise NotImplementedError()

    def compile_interface(self, interface):
        raise NotImplementedError()

    def compile_implementation(self, implementation):
        raise NotImplementedError()

    def compile_range(self, range):
        raise NotImplementedError()

    def compile_struct(self, struct):
        raise NotImplementedError()

    def compile_c_struct(self, c_struct):
        raise NotImplementedError()

    def compile_c_union(self, c_union):
        raise NotImplementedError()

    def compile_module(self):
        for obj in self.module.vars.values():
            if isinstance(obj, types.Enum):
                self.compile_enum(obj)
            elif isinstance(obj, types.FunctionType):
                self.compile_function_type(obj)
            elif isinstance(obj, types.CFunctionType):
                self.compile_c_function_type(obj)
            elif isinstance(obj, types.CBlockFunctionType):
                self.compile_c_block_function_type(obj)
            elif isinstance(obj, types.Function):
                self.compile_function(obj)
            elif isinstance(obj, types.CFunction):
                self.compile_c_function(obj)
            elif isinstance(obj, types.Interface):
                self.compile_interface(obj)
            elif isinstance(obj, types.Range):
                self.compile_range(obj)
            elif isinstance(obj, types.Struct):
                self.compile_struct(obj)
            elif isinstance(obj, types.CStruct):
                self.compile_c_struct(obj)
            elif isinstance(obj, types.CUnion):
                self.compile_c_union(obj)
