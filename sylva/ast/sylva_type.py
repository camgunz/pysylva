from functools import cached_property

from attrs import define, field

from .. import errors
from ..target import get_target
from .attribute_lookup import AttributeLookupMixIn
from .base import Node


@define(eq=False, slots=True)
class BaseSylvaType(Node):

    @cached_property
    def mname(self):
        raise NotImplementedError()


@define(eq=False, slots=True)
class SylvaType(BaseSylvaType, AttributeLookupMixIn):
    llvm_type = field(init=False, default=None)
    implementations = field(init=False, default=[])

    def add_implementation(self, implementation):
        self.implementations.append(implementation)

    def make_constant(self, value):
        return self.llvm_type(value)

    def get_alignment(self):
        llvm_type = self.llvm_type
        return llvm_type.get_abi_alignment(get_target().data)

    def get_size(self):
        return self.llvm_type.get_abi_size(get_target().data)

    def get_pointer(self):
        return self.llvm_type.as_pointer()

    def get_attribute(self, location, name):
        for impl in self.implementations:
            for func in impl.funcs:
                if func.name == name:
                    return func.type
        raise errors.NoSuchAttribute(location, name)

    def emit_attribute_lookup(self, location, module, builder, scope, name):
        for impl in self.implementations:
            for func in impl.funcs:
                if func.name == name:
                    return func
        raise errors.NoSuchAttribute(location, name)


@define(eq=False, slots=True)
class SylvaParamType(BaseSylvaType):
    monomorphizations = field(init=False, default=[])
    implementation_builders = field(init=False, default=[])

    @property
    def is_polymorphic(self):
        return len(self.monomorphizations) > 1

    @property
    def llvm_types(self):
        return [mm.llvm_type for mm in self.monomorphizations]

    def add_monomorphization(self, mm):
        index = len(self.monomorphizations)
        self.monomorphizations.append(mm)
        for ib in self.implementation_builders:
            ib(mm)
        return index

    def add_implementation_builder(self, ib):
        self.implementation_builders.append(ib)
