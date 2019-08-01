class Function:

    def __init__(self, location, name, parameters, return_type, code):
        self.location = location
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.code = code

    @classmethod
    def FromType(cls, location, name, function_type, code):
        return cls(
            location,
            name,
            function_type.parameters,
            function_type.return_type,
            code
        )

    def __repr__(self):
        return 'Function(%r, %r, %r, %r)' % (
            self.name,
            self.parameters,
            self.return_type,
            self.code
        )

    def __str__(self):
        parameters = ', '.join([f'{n}: {t}' for n, t in self.parameters])
        if self.return_type:
            return (
                f'<Function {self.name}({parameters}): {self.return_type}>'
            )
        return f'<Function {self.name}({parameters})>'
