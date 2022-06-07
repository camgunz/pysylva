from functools import cached_property

from .. import errors
from ..target import get_target
from .attribute_lookup import AttributeLookupMixIn
from .base import Node
from .bind import Bind


class BaseSylvaType(Node):

    @cached_property
    def mname(self):
        raise NotImplementedError()


class SylvaType(BaseSylvaType, AttributeLookupMixIn):

    def __init__(self, location):
        BaseSylvaType.__init__(self, location)
        AttributeLookupMixIn.__init__(self)
        self.llvm_type = None
        self.implementations = []

    def __eq__(self, other):
        return isinstance(other, type(self))

    def equals_params(self, *args, **kwargs):
        raise NotImplementedError()

    def add_implementation(self, implementation):
        self.implementations.append(implementation)

    def make_value(self, location, name, value):
        from .value import Value
        return Value(location=location, name=name, value=value, type=self)

    # def make_constant(self, value):
    #     return self.llvm_type(value) # pylint: disable=not-callable

    def get_alignment(self):
        llvm_type = self.llvm_type
        return llvm_type.get_abi_alignment(get_target().data)

    def get_size(self):
        return self.llvm_type.get_abi_size(get_target().data)

    def get_pointer(self):
        return self.llvm_type.as_pointer()

    def emit(self, obj, module, builder, scope, name):
        raise NotImplementedError()


class SylvaParamType(BaseSylvaType):

    PARAMETERS_NAME = 'fields'
    BIND_CLASS = Bind

    def __init__(self, location, binds):
        super().__init__(location)
        self.binds = {b.name: b for b in binds}
        self.monomorphizations = []
        self.implementation_builders = []

    @property
    def is_polymorphic(self):
        return any(b.is_type_parameter for b in self.binds.values())

    @property
    def llvm_types(self):
        return [mm.llvm_type for mm in self.monomorphizations]

    def _build_monomorphization(self, location, binds, bind_types):
        raise NotImplementedError()

    def _bind_type_parameters(self, location, exprs):
        if len(self.binds) != len(exprs):
            raise errors.InvalidParameterization(
                location,
                f'Expected {len(self.binds)} {self.PARAMETERS_NAME}, got '
                f'{len(exprs)}'
            )

        binds = []
        bind_types = {}.fromkeys(self.binds)

        for bind, expr in zip(self.binds.values(), exprs):
            if bind.type is None:
                bind_type = bind_types[bind.name]
                if bind_type is None:
                    bind_types[bind.name] = expr.type
                elif expr.type != bind_type:
                    raise errors.InvalidParameterization(
                        expr.location,
                        f'Cannot parameterize {bind.name} as {expr.type}, '
                        f'already set as {bind_type}'
                    )
                binds.append(
                    self.BIND_CLASS(expr.location, bind.name, expr.type)
                )
            elif bind.type != expr.type:
                raise errors.InvalidParameterization(
                    expr.location,
                    'Type mismatch (expected a value of type "{bind.type}")'
                )
            else:
                binds.append(bind)

        return binds, bind_types

    def _get_or_create_monomorphization_from_binds(
        self, location, binds, bind_types
    ):
        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_binds(binds):
                return n, mm

        mm = self._build_monomorphization(location, binds, bind_types)
        for ib in self.implementation_builders:
            ib(mm)

        index = len(self.monomorphizations)
        self.monomorphizations.append(mm)

        return index, mm

    def add_implementation_builder(self, ib):
        self.implementation_builders.append(ib)

    def get_or_create_monomorphization(self, location, exprs):
        binds, bind_types = self._bind_type_parameters(location, exprs)

        return self._get_or_create_monomorphization_from_binds(
            location, binds, bind_types
        )
