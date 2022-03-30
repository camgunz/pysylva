from antlr4 import FileStream


class Location:

    __slots__ = ('stream', 'index', 'line', 'column')

    def __init__(self, stream, index=0, line=1, column=1):
        self.stream = stream
        self.index = index
        self.line = line
        self.column = column

    @classmethod
    def FromToken(cls, token, stream=None):
        return cls(stream, token.start, token.line, token.column)

    @classmethod
    def FromContext(cls, ctx, stream=None):
        token = ctx.start
        return cls(stream, token.start, token.line, token.column)

    @classmethod
    def Generate(cls):
        return cls(None)

    def __repr__(self):
        if self.is_generated:
            return 'Location(<generated>)'

        return 'Location(%r, %d, %d, %d)' % (
            self.stream, self.index, self.line, self.column
        )

    @property
    def is_generated(self):
        return self.stream is None

    @property
    def is_top(self):
        return self.is_generated or self.index == 0

    @property
    def stream_name(self):
        if self.is_generated:
            return '<generated>'

        if isinstance(self.stream, FileStream):
            return self.stream.fileName

        return self.stream.name

    @property
    def shorthand(self):
        if self.is_generated:
            return '<generated>'

        return '%s:%d:%d' % (self.stream_name, self.line, self.column)

    def pformat(self):
        if self.is_generated:
            return ''

        line_indices = [i for i in range(self.line - 2, self.line) if i >= 0]
        if not line_indices:
            line_indices = [0]

        lines = str(self.stream).splitlines()

        return '\n'.join([lines[i] for i in line_indices if lines[i]] +
                         [('-' * (self.column - 1)) + '^'])
