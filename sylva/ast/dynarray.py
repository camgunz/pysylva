from functools import cached_property

from llvmlite import ir

from ..location import Location
from .array import ArrayType
from .literal import LiteralExpr
from .pointer import (ReferencePointerExpr, ReferencePointerType)
from .sylva_type import SylvaParamType, SylvaType
from .type_mapping import Attribute
from .type_singleton import TypeSingletons
from .value import ValueExpr


class MonoDynarrayType(SylvaType):

    # [NOTE] This isn't a struct with pre-defined fields because Sylva (mostly)
    #        can't represent raw pointers.

    def __init__(self, location, element_type):
        SylvaType.__init__(self, location)
        self.element_type = element_type
        self.llvm_type = ir.LiteralStructType([ # yapf: disable
            TypeSingletons.UINT.value.llvm_type,     # capacity
            TypeSingletons.UINT.value.llvm_type,     # length
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

    def emit_attribute_lookup(self, location, module, builder, scope, name):
        if name == 'capacity':
            return builder.gep(self, [0], inbounds=True, name=name)
        if name == 'length':
            return builder.gep(self, [1], inbounds=True, name=name)
        return SylvaType.emit_attribute_lookup(
            self, location, module, builder, scope, name
        )

    @cached_property
    def mname(self):
        return ''.join(['2da', self.element_type.mangle()])


class DynarrayType(SylvaParamType):

    def get_or_create_monomorphization(self, element_type):
        for mm in self.monomorphizations:
            if mm.element_type != element_type:
                continue
            return mm

        mm = MonoDynarrayType(Location.Generate(), element_type=element_type)

        self.add_monomorphization(mm)

        return mm


# [FIXME] This involves heap allocation
class DynarrayLiteralExpr(LiteralExpr):
    pass


class DynarrayExpr(ValueExpr):

    def get_attribute(self, name):
        if name == 'get_length':
            return Attribute(
                location=Location.Generate(),
                name='get_length',
                type=FunctionType(
                    location=Location.Generate(),
                    monomorphizations=[
                        MonoFunctionType(
                            location=Location.Generate(),
                            parameters=[],
                            return_type=TypeSingletons.UINT.value
                        )
                    ]
                )
            )

    def get_reflection_attribute(self, name):
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return ReferencePointerType(
                referenced_type=ArrayType(
                    Location.Generate(),
                    element_type=TypeSingletons.U8,
                    element_count=self.type.get_size()
                )
            )

    def emit_reflection_lookup(self, location, module, builder, scope, name):
        if name == 'type':
            # [FIXME]
            return self.type
        if name == 'bytes':
            # [NOTE] Just overriding the type here _probably_ works, but only
            #        implicitly. It would be better if we had explicit support
            #        throughout.
            return ReferencePointerExpr(
                location=Location.Generate(),
                type=ReferencePointerType(
                    referenced_type=ArrayType(
                        Location.Generate(),
                        element_type=TypeSingletons.U8,
                        element_count=self.type.get_size()
                    )
                ),
                expr=self
            )
