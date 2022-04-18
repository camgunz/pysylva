from attrs import define

from .stream import Stream


@define(frozen=True, slots=True)
class Location:
    stream: Stream | None = None
    index: int = 0
    line: int = 1
    column: int = 0

    @classmethod
    def FromToken(cls, token, stream=None):
        return cls(stream, token.start_pos, token.line, token.column)

    @classmethod
    def FromContext(cls, ctx, stream=None):
        return cls(stream, ctx.start.start, ctx.start.line, ctx.start.column)

    @classmethod
    def FromTree(cls, tree, stream=None):
        md = tree.data
        return cls(stream, md.start_pos, md.line, md.column)

    @classmethod
    def Generate(cls):
        return cls()

    def __repr__(self):
        if self.is_generated:
            return 'Location(<generated>)'

        return 'Location(%r, %d, %d, %d)' % (
            self.stream_name, self.index, self.line, self.column
        )

    def __str__(self):
        return self.shorthand

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
                         [('-' * self.column) + '^'])
