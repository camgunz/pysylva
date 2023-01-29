from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional, Union

from sylva import errors, utils
from sylva.ast.expr import Expr
from sylva.ast.parameter import Parameter
from sylva.ast.statement import Stmt
from sylva.ast.sylva_type import MonoType, ParamType, SylvaType
from sylva.ast.value import Value


@dataclass(kw_only=True)
class FnType(SylvaType):
    parameters: list[Parameter] = field(default_factory=list)
    return_type: Optional[SylvaType] = field(default=None)


@dataclass(kw_only=True)
class MonoFnType(FnType, MonoType):

    def __post_init__(self):
        dupes = utils.get_dupes(p.name for p in self.parameters)
        if dupes:
            raise errors.DuplicateParameters(self, dupes)

    @cached_property
    def mname(self):
        return ''.join([
            '2fn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


@dataclass(kw_only=True)
class ParamFnType(FnType, ParamType):
    return_type_param: Optional[Parameter] = field(default=None)
    return_type_is_type_parameter: bool = field(init=False, default=False)
    return_type_param_name: Optional[str] = field(init=False, default=None)
    _type_parameters: list[str] = field(init=False, default_factory=list)
    return_type_must_be_inferred: bool = field(init=False, default=False)

    def __post_init__(self):
        self.return_type_is_type_parameter = (
            self.return_type_param and self.return_type_param.is_type_parameter
        )

        self.return_type = (
            None if not self.return_type_param else self.return_type_param.type
        )

        self.return_type_param_name = (
            None if not self.return_type_param else self.return_type_param.name
        )

        self._type_parameters = [
            p.name for p in self.parameters if p.is_type_parameter
        ]

        self.return_type_must_be_inferred = (
            self.return_type_is_type_parameter and
            self.return_type_param.name not in self._type_parameters
        )

        if self.return_type_is_type_parameter:
            self._type_parameters.append(self.return_type)

    @property
    def type_parameters(self):
        return self._type_parameters

    # pylint: disable=arguments-differ
    def get_or_create_monomorphization(
        self, location, parameters, return_type
    ):
        if self.return_type_must_be_inferred and return_type is None:
            raise errors.InvalidParameterization(
                location,
                'Cannot parameterize function return type; return type could '
                'not be inferred, and its type parameter '
                f'"{self.return_type_param_name}" was not found in function '
                'parameters'
            )

        if len(self.parameters) != len(parameters):
            raise errors.InvalidParameterization(
                location,
                f'Expected {len(self.parameters)} parameters, got '
                f'{len(parameters)}'
            )

        param_types = {}
        bound_params = []
        for sp, p in zip(self.parameters, parameters):
            if sp.is_type_parameter:
                param_type = param_types.get(sp.name)
                if param_type is None:
                    param_types = p.type
                elif p.type != param_type:
                    raise errors.InvalidParameterization(
                        p.location,
                        f'Cannot parameterize {p.name} as {p.type}, already '
                        f'set as {param_type}'
                    )
                bound_params.append(Parameter(p.location, sp.name, p.type))
            elif sp.type != p.type:
                raise errors.InvalidParameterization(
                    p.location,
                    f'Type mismatch (expected a value of type "{sp.type}", '
                    f'got "{p.type}"'
                )
            else:
                bound_params.append(sp)

        if return_type is None:
            if self.return_type_is_type_parameter:
                return_type = param_types.get(self.return_type_param_name)
            else:
                return_type = self.return_type

        for n, mm in enumerate(self.monomorphizations):
            if mm.equals_params(bound_params, return_type):
                return n, mm

        index = len(self.monomorphizations)

        mm = MonoFnType(
            name=self.name,
            location=location,
            parameters=bound_params,
            return_type=return_type
        )
        self.monomorphizations.append(mm)

        return index, mm


@dataclass(kw_only=True)
class Fn(Value):
    value: list[Union[Expr | Stmt]] = field(default_factory=list)
