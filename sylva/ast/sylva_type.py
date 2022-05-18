import typing

from attrs import define

from . import ast


@define(eq=False, slots=True)
class SylvaType(ast.ASTNode):
    implementations: typing.List = []

    def mangle(self):
        raise NotImplementedError()

    def add_implementation(self, implementation):
        self.implementations.append(implementation)


@define(eq=False, slots=True)
class LLVMTypeMixIn:

    def make_constant(self, module, value):
        return self.get_llvm_type(module)(value)

    def get_alignment(self, module):
        llvm_type = self.get_llvm_type(module)
        return llvm_type.get_abi_alignment(module.target.data)

    def get_size(self, module):
        return self.get_llvm_type(module).get_abi_size(module.target.data)

    def get_pointer(self, module):
        return self.get_llvm_type(module).as_pointer()

    def get_llvm_type(self, module):
        raise NotImplementedError()


@define(eq=False, slots=True)
class ParamTypeMixIn:
    monomorphizations: typing.List = []

    @property
    def is_polymorphic(self):
        return len(self.monomorphizations) > 1

    def get_llvm_types(self, module):
        raise NotImplementedError()
