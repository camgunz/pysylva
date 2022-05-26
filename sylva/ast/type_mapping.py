from attrs import define, field

from .base import Node


@define(eq=False, slots=True)
class BaseTypeMapping(Node):
    name = field()
    type = field()
    index = field(default=None)

    @property
    def handle(self):
        return self.index if self.index is not None else self.name

    def emit(self, obj, module, builder, scope):
        raise NotImplementedError()


@define(eq=False, slots=True)
class Parameter(BaseTypeMapping):

    def emit(self, obj, module, builder, scope):
        return builder.alloca(self.type.llvm_type, name=self.name)


@define(eq=False, slots=True)
class Attribute(BaseTypeMapping):
    func = field()
    index = field(init=False, default=None)

    def emit(self, obj, module, builder, scope):
        return self.func(obj, self.location, module, builder, scope)


@define(eq=False, slots=True)
class Field(BaseTypeMapping):

    def emit(self, obj, module, builder, scope):
        return builder.gep(obj, [self.index], inbounds=True)
