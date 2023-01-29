import enum

from dataclasses import dataclass, field
from functools import cached_property

from sylva import errors
from sylva.ast.node import Node


class TypeModifier(enum.Enum):
    NoMod = enum.auto()
    Ptr = enum.auto()
    Ref = enum.auto()
    ExRef = enum.auto()

    @classmethod
    def FromTypeLiteral(cls, type_literal):
        first_child = type_literal.children[0].getText()
        last_child = type_literal.children[-1].getText()

        if first_child == '*':
            return cls.Ptr

        if not first_child == '&':
            return cls.NoMod

        if last_child == '!':
            return cls.ExRef

        return cls.Ref


@dataclass(kw_only=True)
class SylvaType(Node):
    mod: TypeModifier = TypeModifier.NoMod

    @cached_property
    def mname(self):
        raise NotImplementedError()


@dataclass(kw_only=True)
class PtrType(SylvaType):
    mod: TypeModifier = field(init=False, default=TypeModifier.Ptr)


@dataclass(kw_only=True)
class RefType(SylvaType):
    mod: TypeModifier = field(init=False, default=TypeModifier.Ref)


@dataclass(kw_only=True)
class ExRefType(SylvaType):
    mod: TypeModifier = field(init=False, default=TypeModifier.ExRef)


@dataclass(kw_only=True)
class MonoType(SylvaType):
    implementations: list = field(default_factory=list)

    @property
    def type_parameters(self):
        return []

    def __eq__(self, other):
        return isinstance(other, type(self)) # [FIXME] ???

    def add_implementation(self, implementation):
        self.implementations.append(implementation)


@dataclass(kw_only=True)
class ParamType(SylvaType):
    monomorphizations: list = field(default_factory=list)

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

    def equals_params(self, *args, **kwargs):
        raise NotImplementedError()

    @property
    def type_parameters(self):
        raise NotImplementedError()

    def get_or_create_monomorphization(self, location, *args, **kwargs):
        raise NotImplementedError()


@dataclass(kw_only=True)
class TypeDef(Node):
    name: str
    type: SylvaType


@dataclass(kw_only=True)
class TypeParam(Node):
    name: str
