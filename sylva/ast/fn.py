from functools import cached_property

from llvmlite import ir

from .. import errors, utils
from .defs import ParamTypeDef
from .parameter import Parameter
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
        return SylvaType.__eq__(self, other) and self.equals_params(
            other.parameters, other.return_type
        )

    # pylint: disable=arguments-differ
    def equals_params(self, parameters, return_type):
        return ( # yapf: disable
            len(self.parameters) == len(parameters) and
            all(
                p.name == op.name and p.type == op.type
                for p, op in zip(self.parameters, parameters)
            ) and
            self.return_type == return_type
        )

    @cached_property
    def mname(self):
        return ''.join([
            '2fn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


class FnType(SylvaParamType):

    def __init__(self, location, parameters, return_type_param):
        SylvaParamType.__init__(self, location)
        self.parameters = parameters

        self.return_type_is_type_parameter = (
            return_type_param and return_type_param.is_type_parameter
        )

        self.return_type = (
            None if not return_type_param else return_type_param.type
        )

        self.return_type_param_name = (
            None if not return_type_param else return_type_param.name
        )

        self._type_parameters = [
            p.name for p in self.parameters if p.is_type_parameter
        ]

        self.return_type_must_be_inferred = (
            self.return_type_is_type_parameter and
            return_type_param.name not in self._type_parameters
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
            location=location,
            parameters=bound_params,
            return_type=return_type
        )
        self.monomorphizations.append(mm)

        return index, mm


class Fn(ParamTypeDef):

    def __init__(self, location, name, type, code):
        ParamTypeDef.__init__(self, location, name, type)
        self.code = code
        self.llvm_value = None

    def get_llvm_value(self, *args, **kwargs):
        if self.llvm_value:
            return self.llvm_value

        module = kwargs['module']
        llvm_module = module.type.llvm_type

        # [TODO] Get the right monomorphization here
        func = ir.Function(llvm_module, self.type.llvm_type, name=self.name)

        kwargs['block'] = func.append_basic_block()
        kwargs['builder'] = ir.IRBuilder(block=kwargs['block'])
        kwargs['scope'] = {}

        for arg, param in zip(func.args, self.type.parameters):
            param.emit(arg=arg, *args, **kwargs)

        for node in self.code:
            node.emit(func=self, *args, **kwargs)

        self.llvm_value = func

        return self.llvm_value

    # def emit(self, obj, module, builder, scope, name):
    #     llvm_module = module.type.llvm_type
    #     # [TODO] Get the right monomorphization here
    #     llvm_func_type = self.type.llvm_type
    #     llvm_func = ir.Function(llvm_module, llvm_func_type, name=self.name)
