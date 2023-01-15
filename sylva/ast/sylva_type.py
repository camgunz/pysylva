from functools import cached_property

from .. import errors
from ..target import get_target
from .attribute_lookup import AttributeLookupMixIn
from .base import Node


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

    @property
    def type_parameters(self):
        return []

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

    def __init__(self, location):
        super().__init__(location)
        self.monomorphizations = []
        self.implementation_builders = []

    def get_parameterized_types(self, location, binds, arguments):
        if len(self.type_parameters) != len(arguments):
            raise errors.InvalidParameterization(
                location,
                f'Expected {len(self.type_parameters)} type parameters, got '
                f'{len(arguments)}'
            )

        type_args = {}
        for a in arguments:
            if a.name in type_args:
                raise errors.InvalidParameterization(
                    a.location, f'Duplicate type parameter "{a.name}"'
                )
            type_args[a.name] = a

        types = []
        for b in binds:
            if not b.is_type_parameter:
                types.append(b)
            else:
                bind_type = type_args.get(b.name)
                if bind_type is None:
                    raise errors.InvalidParameterization(
                        location, f'Missing type parameter for {b.name}'
                    )
                types.append(bind_type)

        return types

    def get_parameterized_types_from_expressions(
        self, location, binds, arg_exprs
    ):
        if len(binds) != len(arg_exprs):
            raise errors.InvalidParameterization(
                location,
                f'Expected {len(binds)} type parameters, got {len(arg_exprs)}'
            )

        args = []
        for b, ae in zip(binds, arg_exprs):
            if b.is_type_parameter:
                args.append(ae)
            elif b.type != ae.type:
                raise errors.InvalidParameterization(
                    ae.location,
                    f'Type mismatch: expected a value of type "{b.type}"; got '
                    f'"{ae.type}"'
                )
        return self.get_parameterized_types(location, binds, args)

    @property
    def type_parameters(self):
        raise NotImplementedError()

    @property
    def llvm_types(self):
        return [mm.llvm_type for mm in self.monomorphizations]

    def add_implementation_builder(self, ib):
        self.implementation_builders.append(ib)

    def get_or_create_monomorphization(self, location, *args, **kwargs):
        raise NotImplementedError()
