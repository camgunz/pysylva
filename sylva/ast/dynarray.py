from functools import cached_property

from llvmlite import ir

from .. import errors
from ..location import Location
from .attribute import Attribute
from .attribute_lookup import AttributeLookupExpr
from .fn import Fn, MonoFnType
from .impl import Impl
from .literal import LiteralExpr
from .lookup import LookupExpr
from .statement import ReturnStmt
from .sylva_type import SylvaParamType, SylvaType


def dynarray_implementation_builder(dynarray_type):
    from .type_singleton import IfaceSingletons, TypeSingletons

    str_eight = TypeSingletons.STR.get_or_create_monomorphization(
        Location.Generate(), 8
    )

    # pylint: disable=unused-argument
    def emit_name_param(obj, location, module, builder, scope):
        return ir.Constant(
            str_eight.llvm_type, bytearray('dynarray', encoding='utf-8')
        )

    dynarray_type.set_attribute(
        Attribute(
            location=Location.Generate(),
            name='name',
            type=str_eight,
            func=emit_name_param
        )
    )

    get_length = Fn(
        location=Location.Generate(),
        name='get_length',
        type=MonoFnType(
            location=Location.Generate(),
            parameters=[],
            return_type=TypeSingletons.UINT
        ),
        code=[
            ReturnStmt(
                location=Location.Generate(),
                expr=AttributeLookupExpr(
                    location=Location.Generate(),
                    type=TypeSingletons.UINT,
                    name='length',
                    obj=LookupExpr(
                        location=Location.Generate(),
                        name='self',
                        type=dynarray_type
                    ),
                )
            )
        ]
    )

    impl = Impl(
        location=Location.Generate(),
        interface=IfaceSingletons.ARRAY.value,
        implementing_type=dynarray_type,
        funcs=[get_length]
    )

    IfaceSingletons.ARRAY.value.add_implementation(impl)
    dynarray_type.add_implementation(impl)


class MonoDynarrayType(SylvaType):

    # [NOTE] This isn't a struct with pre-defined fields because Sylva (mostly)
    #        can't represent raw pointers.

    def __init__(self, location, element_type):
        from .type_singleton import TypeSingletons

        SylvaType.__init__(self, location)
        self.element_type = element_type
        self.llvm_type = ir.LiteralStructType([ # yapf: disable
            TypeSingletons.UINT.llvm_type,     # capacity
            TypeSingletons.UINT.llvm_type,     # length
            self.element_type.llvm_type.as_pointer() # data
        ])

    # def get_reflection_attribute(self, location, name):
    #     if name == 'name':
    #         return StrType
    #     if name == 'size':
    #         return IntType
    #     if name == 'element_type':
    #         return self.element_type.type

    # def emit_reflection_lookup(self, location, module, builder, scope, name):
    #     # [FIXME] These need to be Sylva expressions that evaluate to LLVM
    #     #         values
    #     if name == 'name':
    #         return 'dynarray'
    #     if name == 'size':
    #         return self.get_size()
    #     if name == 'element_type':
    #         return self.element_type.llvm_type

    def emit_attribute_lookup(self, module, builder, scope, name):
        if name == 'capacity':
            return builder.gep(self, [0], inbounds=True, name=name)
        if name == 'length':
            return builder.gep(self, [1], inbounds=True, name=name)
        return SylvaType.emit_attribute_lookup(
            self, module, builder, scope, name
        )

    @cached_property
    def mname(self):
        return ''.join(['2da', self.element_type.mname])

    def __eq__(self, other):
        return (
            SylvaType.__eq__(self, other) and
            self.equals_params(other.element_type)
        )

    # pylint: disable=arguments-differ
    def equals_params(self, element_type):
        return self.element_type == element_type

    def equals_binds(self, binds):
        return self.equals_params(binds[0].value)


class DynarrayType(SylvaParamType):

    def __init__(self, location):
        SylvaParamType.__init__(
            self,
            location, [self.BIND_CLASS(Location.Generate(), 'element_type')]
        )
        self.add_implementation_builder(dynarray_implementation_builder)

    def _build_monomorphization(self, location, binds, bind_types):
        return MonoDynarrayType(location, element_type=binds[0].value)

    def _bind_type_parameters(self, location, exprs):
        binds, bind_types = SylvaParamType._bind_type_parameters(
            self, location, exprs
        )
        if not bind_types['element_type'] == SylvaType:
            raise errors.InvalidParameterization(
                exprs[0].location,
                'Type mismatch (expected a value of type "type")'
            )

        return binds, bind_types


# [FIXME] This involves heap allocation
class DynarrayLiteralExpr(LiteralExpr):
    pass
