from ..location import Location
from .attribute_lookup import AttributeLookupMixIn
from .base import Node
from .reflection_lookup import ReflectionLookupMixIn
from .sylva_type import SylvaType
from .type_singleton import TypeSingletons


class Value(Node, AttributeLookupMixIn, ReflectionLookupMixIn):

    def __init__(self, location, name, value, type):
        Node.__init__(self, location)
        AttributeLookupMixIn.__init__(self)
        ReflectionLookupMixIn.__init__(self)
        self.name = name
        self.value = value
        self.type = type

    # pylint: disable=unused-argument
    def emit(self, module, builder, scope):
        return builder.load(self.value, self.name)

    def get_attribute(self, name):
        for impl in self.type.implementations:
            for func in impl.funcs:
                if func.name == name:
                    return func.type
        return AttributeLookupMixIn.get_attribute(self, name)

    def emit_attribute_lookup(self, module, builder, scope, name):
        for impl in self.type.implementations:
            for func in impl.funcs:
                if func.name == name:
                    return Value(
                        location=func.location,
                        name=name,
                        type=func.type,
                        value=func
                    )
        return AttributeLookupMixIn.emit_attribute_lookup(
            self, module, builder, scope, name
        )

    def get_reflection_attribute(self, name):
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return TypeSingletons.POINTER.value.get_or_create_monomorphization(
                referenced_type=TypeSingletons.ARRAY.value
                .get_or_create_monomorphization(
                    element_type=TypeSingletons.U8.value,
                    element_count=self.type.get_size()
                ),
                is_reference=True,
                is_exclusive=False
            )

    def emit_reflection_lookup(self, module, builder, scope, name):
        if name == 'type':
            return self.type # [FIXME]
        if name == 'bytes':
            # [NOTE] Just overriding the type here _probably_ works, but only
            #        implicitly. It would be better if we had explicit support
            #        throughout.
            return Value(
                location=Location.Generate(),
                name=name,
                type=TypeSingletons.POINTER.value
                .get_or_create_monomorphization(
                    referenced_type=TypeSingletons.ARRAY.value
                    .get_or_create_monomorphization(
                        element_type=TypeSingletons.U8.value,
                        element_count=self.type.get_size()
                    ),
                    is_reference=True,
                    is_exclusive=False
                ),
                value=self.get_bytes()
            )

    def get_bytes(self):
        raise NotImplementedError()
