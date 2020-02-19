class Scalar:

    def __init__(self, value):
        self.value = value


class Boolean(Scalar):
    # Booleans are the native integer type
    pass


class Rune(Scalar):
    pass


class String(Scalar):
    pass


class Decimal(Scalar):

    __slots__ = ('value', 'rounding_mode')

    def __init__(self, value, rounding_mode):
        super().__init__(value)
        self.rounding_mode = rounding_mode


class Float(Scalar):

    __slots__ = ('value', 'bits', 'rounding_mode')

    def __init__(self, value, bits, rounding_mode):
        super().__init__(value)
        self.bits = bits
        self.rounding_mode = rounding_mode


class Integer(Scalar):

    __slots__ = (
        'value', 'signed', 'bits', 'overflow_handler', 'rounding_mode', 'base'
    )

    def __init__(self, value, signed, bits, overflow_handler, base):
        super().__init__(value)
        self.signed = signed
        self.bits = bits
        self.overflow_handler = overflow_handler
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
