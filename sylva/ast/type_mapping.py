from .base import Node


class BaseTypeMapping(Node):

    def __init__(self, location, name, type, index=None):
        Node.__init__(self, location)
        self.name = name
        self.type = type
        self.index = index

    @property
    def handle(self):
        return self.index if self.index is not None else self.name

    def emit(self, obj, module, builder, scope):
        raise NotImplementedError()

    def make_value(self, value):
        return self.type.make_value(
            location=self.location, name=self.name, value=value
        )


class Parameter(BaseTypeMapping):

    def emit(self, obj, module, builder, scope):
        return builder.alloca(self.type.llvm_type, name=self.name)


class Attribute(BaseTypeMapping):

    def __init__(self, location, name, type, func=None):
        BaseTypeMapping.__init__(self, location, name, type)
        self.func = func

    def emit(self, obj, module, builder, scope):
        if not self.func:
            raise Exception(f'Attribute {self.name} has no action')
        return self.func(obj, self.location, module, builder, scope)


class Field(BaseTypeMapping):

    # pylint: disable=arguments-differ
    def emit(self, obj, module, builder, scope, name):
        return builder.gep(obj, [self.index], inbounds=True, name=name)
