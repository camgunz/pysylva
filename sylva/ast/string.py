from functools import cached_property

from attrs import define, field

from ..location import Location
from .attribute_lookup import AttributeLookupExpr, AttributeLookupMixIn
from .dynarray import DynarrayExpr, MonoDynarrayType
from .function import FunctionDef, MonoFunctionType
from .implementation import Implementation
from .lookup import LookupExpr
from .pointer import ReferencePointerType
from .statement import ReturnStmt
from .str import StrType
from .type_mapping import Parameter
from .type_singleton import IfaceSingletons, TypeSingletons


def string_implementation_builder(string_type):
    get_length = FunctionDef(
        name='get_length',
        type=MonoFunctionType(
            parameters=[
                Parameter(
                    location=Location.Generate(),
                    name='self',
                    type=ReferencePointerType(
                        referenced_type=string_type,
                        is_exclusive=False,
                    )
                )
            ],
            return_type=TypeSingletons.UINT.value
        ),
        code=[
            ReturnStmt(
                expr=AttributeLookupExpr(
                    location=Location.Generate(),
                    type=TypeSingletons.UINT.value,
                    attribute='len',
                    expr=LookupExpr( # yapf: disable
                        location=Location.Generate(),
                        name='self'
                    ),
                    reflection=False
                )
            )
        ]
    )

    string_impl = Implementation(
        location=Location.Generate(),
        interface=IfaceSingletons.STRING.value,
        implementing_type=string_type,
        funcs=[get_length]
    )

    IfaceSingletons.STRING.value.add_implementation(string_impl)
    string_type.add_implementation(string_impl)


@define(eq=False, slots=True)
class StringType(MonoDynarrayType, AttributeLookupMixIn):
    implementations = field(
        init=False, default=[string_implementation_builder]
    )

    @llvm_type.default # noqa: F821
    def _llvm_type_factory(self):
        return MonoDynarrayType(element_type=TypeSingletons.U8.value).llvm_type

    def get_reflection_attribute(self, location, name):
        if name == 'name':
            return StrType(
                location=Location.Generate(),
                value=bytearray('string', encoding='utf-8'),
            )
        if name == 'size':
            return TypeSingletons.UINT.value

    def emit_reflection_lookup(self, location, module, builder, scope, name):
        if name == 'name':
            return 'string'
        if name == 'size':
            return self.get_size()

    def get_value_expr(self, location):
        return StringExpr(location=location, type=self)

    @cached_property
    def mname(self):
        return '6string'


@define(eq=False, slots=True)
class StringExpr(DynarrayExpr, AttributeLookupMixIn):
    pass
