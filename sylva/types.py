class Scalar:

    def __init__(self, value):
        self.value = value


class Boolean(Scalar):
    pass


class Rune(Scalar):
    pass


class String(Scalar):
    pass


class Decimal(Scalar):

    def __init__(self, value, rounding_mode):
        super().__init__(value)
        self.rounding_mode = rounding_mode


class Float(Scalar):

    def __init__(self, value, rounding_mode):
        super().__init__(value)
        self.rounding_mode = rounding_mode


class Integer(Scalar):

    def __init__(self, value, overflow_handler, signed, base):
        super().__init__(value)
        self.overflow_handler = overflow_handler
        self.signed = signed
        self.base = base


class Struct:

    def __init__(self, location, name, fields):
        self.location = location
        self.name = name
        self.fields = fields

    def __repr__(self):
        return 'Struct(%r, %r, %r)' % (
            self.location,
            self.name,
            self.fields
        )

    def __str__(self):
        fields = ', '.join([f'{name}: {type}' for name, type in self.fields])
        return f'<Struct {self.name} {{{fields}}}>'


class Array:

    def __init__(self, location, name, element_type, element_count):
        self.location = location
        self.name = name
        self.element_type = element_type
        self.element_count = element_count

    def __repr__(self):
        return 'Array(%r, %r, %r, %r)' % (
            self.location,
            self.name,
            self.element_type,
            self.element_count
        )

    def __str__(self):
        if self.element_count:
            return (
                f'<Array {self.name} '
                f'[{self.element_type} * {self.element_count}]>'
            )
        return f'<Array {self.name} [{self.element_type}]>'


class FunctionType:

    def __init__(self, location, name, parameters, return_type):
        self.location = location
        self.name = name
        self.parameters = parameters
        self.return_type = return_type

    def __repr__(self):
        return 'FunctionType(%r, %r, %r)' % (
            self.name,
            self.parameters,
            self.return_type
        )

    def __str__(self):
        parameters = ', '.join([f'{n}: {t}' for n, t in self.parameters])
        if self.return_type:
            return (
                f'<FunctionType {self.name}({parameters}): {self.return_type}>'
            )
        return f'<FunctionType {self.name}({parameters})>'
