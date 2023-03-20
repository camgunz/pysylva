from dataclasses import dataclass

from sylva.stream import Stream


@dataclass(slots=True, frozen=True)
class Location:
    stream: Stream | None = None
    index: int = 0
    line: int = 1
    column: int = 1

    @classmethod
    def FromToken(cls, token, stream=None):
        return cls(stream, token.start_pos, token.line, token.column)

    @classmethod
    def FromContext(cls, ctx, stream=None):
        return cls(stream, ctx.start.start, ctx.start.line, ctx.start.column)

    @classmethod
    def FromMeta(cls, meta, stream=None):
        return cls(stream, meta.start_pos, meta.line, meta.column)

    @classmethod
    def FromTree(cls, tree, stream=None):
        return cls.FromMeta(tree.meta, stream=stream)

    @classmethod
    def FromPath(cls, path):
        return cls(stream=Stream.FromPath(path))

    @classmethod
    def FromLarkError(cls, err, stream=None):
        return cls(
            stream=stream,
            index=err.pos_in_stream,
            line=err.line,
            column=err.column
        )

    @classmethod
    def Generate(cls):
        return cls()

    def __repr__(self):
        return self.shorthand

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

    def copy(self):
        return Location(
            stream=self.stream,
            index=self.index,
            line=self.line,
            column=self.column
        )

    def pformat(self):
        if self.is_generated:
            return ''

        line_indices = [i for i in range(self.line - 2, self.line) if i >= 0]
        if not line_indices:
            line_indices = [0]

        lines = self.stream.data.splitlines()

        return '\n'.join([lines[i] for i in line_indices if lines[i]] +
                         [('-' * (self.column - 1)) + '^'])
