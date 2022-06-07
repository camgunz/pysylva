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

    def equals_binds(self, binds):
        return self.equals_params(binds[:-1], binds[-1].type)

    @cached_property
    def mname(self):
        return ''.join([
            '2fn',
            ''.join(p.type.mname for p in self.parameters),
            self.return_type.mname if self.return_type else '1v'
        ])


class FnType(SylvaParamType):

    BIND_CLASS = Parameter

    def __init__(self, location, parameters, return_type_param):
        SylvaParamType.__init__(self, location, parameters)
        self.parameters = parameters
        self.return_type_param = return_type_param
        self.return_type_is_type_parameter = (
            self.return_type_param.is_type_parameter
        )
        self.return_type = self.return_type_param.type
        self.return_type_must_be_inferred = (
            self.return_type_is_type_parameter and self.return_type_param.name
            not in [p.name for p in parameters if p.is_type_parameter]
        )

    def _build_monomorphization(self, location, binds, bind_types):
        return MonoFnType(location, binds[:-1], binds[-1].type)

    # pylint: disable=arguments-differ
    def get_or_create_monomorphization(self, location, exprs, return_type):
        if self.return_type_must_be_inferred and return_type is None:
            raise errors.InvalidParameterization(
                location,
                'Cannot parameterize function return type; return type could '
                'not be inferred, and its type parameter '
                f'"{self.return_type_param.name}" was not found in function '
                'parameters'
            )

        binds, bind_types = self._bind_type_parameters(location, exprs)

        if self.return_type_must_be_inferred:
            binds.append(
                self.BIND_CLASS(location, name=None, type=return_type)
            )
        elif self.return_type_is_type_parameter:
            binds.append(
                self.BIND_CLASS(
                    location=location,
                    name=None,
                    type=bind_types[self.return_type_param.name]
                )
            )
        else:
            binds.append(
                self.BIND_CLASS(location, name=None, type=self.return_type)
            )

        return self._get_or_create_monomorphization_from_binds(
            location, binds, bind_types
        )


class Fn(ParamTypeDef):

    def __init__(self, location, name, type, code):
        ParamTypeDef.__init__(self, location, name, type)
        self.code = code

    def emit(self, obj, module, builder, scope, name):
        llvm_module = module.type.llvm_type
        # [TODO] Get the right monomorphization here
        llvm_func_type = self.type.emit(llvm_module)
        llvm_func = ir.Function(llvm_module, llvm_func_type, name=self.name)
        block = llvm_func.append_basic_block()
        builder = ir.IRBuilder(block=block)
        scope = {}
        for arg, param in zip(llvm_func_type.args, self.type.parameters):
            param.emit(arg, None, builder, scope)
        for node in self.code:
            node.emit(self, llvm_module, builder, scope)
