import typing

from functools import cached_property

from attrs import define, field
from llvmlite import ir # type: ignore

from ..target import get_target
from .base import Node


@define(eq=False, slots=True)
class BaseSylvaType(Node):

    @cached_property
    def mname(self):
        raise NotImplementedError()


@define(eq=False, slots=True)
class SylvaType(BaseSylvaType):
    llvm_type: ir.Type | None = field(init=False, default=None)
    implementations: typing.List = []

    def add_implementation(self, implementation):
        self.implementations.append(implementation)

    def make_constant(self, value):
        # pylint: disable=not-callable
        return self.llvm_type(value)

    def get_alignment(self):
        # pylint: disable=no-member
        llvm_type = self.llvm_type
        return llvm_type.get_abi_alignment(get_target().data)

    def get_size(self):
        # pylint: disable=no-member
        return self.llvm_type.get_abi_size(get_target().data)

    def get_pointer(self):
        # pylint: disable=no-member
        return self.llvm_type.as_pointer()


@define(eq=False, slots=True)
class SylvaParamType(BaseSylvaType):
    monomorphizations: typing.List = []
    implementation_builders: typing.List = []

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
