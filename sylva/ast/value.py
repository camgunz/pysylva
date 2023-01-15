from ..location import Location
from .attribute_lookup import AttributeLookupMixIn
from .bind import Bind
from .reflection_lookup import ReflectionLookupMixIn
from .sylva_type import SylvaType


class Value(Bind, AttributeLookupMixIn, ReflectionLookupMixIn):

    def __init__(self, location, name, type, value):
        Bind.__init__(self, location, name, type)
        AttributeLookupMixIn.__init__(self)
        ReflectionLookupMixIn.__init__(self)
        self.value = value

    # pylint: disable=unused-argument
    def emit(self, obj, module, builder, scope, name):
        alloca = builder.alloca(self.type.llvm_type, self.name)
        builder.store(self.value, alloca)
        scope[self.name] = self
        return self.value

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
        from .type_singleton import TypeSingletons

        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return TypeSingletons.POINTER.get_or_create_monomorphization(
                location=Location.Generate(),
                referenced_type=TypeSingletons.ARRAY
                .get_or_create_monomorphization(
                    location=Location.Generate(),
                    element_type=TypeSingletons.U8,
                    element_count=self.type.get_size()
                )[1],
                is_reference=True,
                is_exclusive=False
            )[1]

    def emit_reflection_lookup(self, module, builder, scope, name):
        from .type_singleton import TypeSingletons

        if name == 'type':
            return self.type # [FIXME]
        if name == 'bytes':
            # [NOTE] Just overriding the type here _probably_ works, but only
            #        implicitly. It would be better if we had explicit support
            #        throughout.
            return Value(
                location=Location.Generate(),
                name=name,
                type=TypeSingletons.POINTER.get_or_create_monomorphization(
                    location=Location.Generate(),
                    referenced_type=TypeSingletons.ARRAY
                    .get_or_create_monomorphization(
                        location=Location.Generate(),
                        element_type=TypeSingletons.U8,
                        element_count=self.type.get_size()
                    )[1],
                    is_reference=True,
                    is_exclusive=False
                )[1],
                value=self.get_bytes()
            )

    def get_bytes(self):
        raise NotImplementedError()
