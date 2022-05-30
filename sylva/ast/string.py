from functools import cached_property

from ..location import Location
from .attribute_lookup import AttributeLookupExpr
from .dynarray import MonoDynarrayType
from .fn import Fn, MonoFnType
from .impl import Impl
from .lookup import LookupExpr
from .parameter import Parameter
from .statement import ReturnStmt


def string_impl_builder(string_type):
    from .type_singleton import IfaceSingletons, TypeSingletons

    get_length = Fn(
        location=Location.Generate(),
        name='get_length',
        type=MonoFnType(
            location=Location.Generate(),
            parameters=[
                Parameter(
                    location=Location.Generate(),
                    name='self',
                    type=TypeSingletons.POINTER
                    .get_or_create_monomorphization(
                        Location.Generate(),
                        referenced_type=string_type,
                        is_reference=True,
                        is_exclusive=False
                    )
                )
            ],
            return_type=TypeSingletons.UINT
        ),
        code=[
            ReturnStmt(
                location=Location.Generate(),
                expr=AttributeLookupExpr(
                    location=Location.Generate(),
                    type=TypeSingletons.UINT,
                    name='len',
                    obj=LookupExpr( # yapf: disable
                        location=Location.Generate(),
                        type=string_type,
                        name='self',
                    ),
                )
            )
        ]
    )

    string_impl = Impl(
        location=Location.Generate(),
        interface=IfaceSingletons.STRING.value,
        implementing_type=string_type,
        funcs=[get_length]
    )

    IfaceSingletons.STRING.value.add_implementation(string_impl)
    string_type.add_impl(string_impl)


class StringType(MonoDynarrayType):

    def __init__(self, location):
        from .type_singleton import TypeSingletons

        MonoDynarrayType.__init__(self, location, TypeSingletons.U8)
        self.implementations = [string_impl_builder]

    # def get_reflection_attribute(self, location, name):
    #     if name == 'name':
    #         return StrType(
    #             location=Location.Generate(),
    #             value=bytearray('string', encoding='utf-8'),
    #         )
    #     if name == 'size':
    #         return TypeSingletons.UINT

    # def emit_reflection_lookup(self, location, module, builder, scope, name):
    #     if name == 'name':
    #         return 'string'
    #     if name == 'size':
    #         return self.get_size()

    @cached_property
    def mname(self):
        return '6string'
