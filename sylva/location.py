from functools import total_ordering


@total_ordering
class Location:

    __slots__ = ('data_source', 'index', 'line', 'column')

    def __init__(self, data_source, index=0, line=1, column=1):
        self.data_source = data_source
        self.index = index
        self.line = line
        self.column = column

    @classmethod
    def Generate(cls):
        return cls(None)

    def __eq__(self, other):
        return (
            self.data_source == other.data_source and
            self.index == other.index
        )

    def __lt__(self, other):
        if not isinstance(other, Location):
            return NotImplemented
        return (
            self.data_source == other.data_source and self.index < other.index
        )

    def __repr__(self):
        if self.is_generated:
            return 'Location(<generated>)'
        return 'Location(%r, %d, %d, %d)' % (
            self.data_source, self.index, self.line, self.column
        )

    @property
    def is_beginning(self):
        return self.is_generated or self.index == 0

    @property
    def is_generated(self):
        return self.data_source is None

    @property
    def data_source_name(self):
        if self.is_generated:
            return '<generated>'
        return self.data_source.name

    @property
    def shorthand(self):
        if self.is_generated:
            return '<generated>'
        return '%s:%d:%d' % (
            self.data_source_name, self.line, self.column
        )

    def copy(self):
        return Location(self.data_source, self.index, self.line, self.column)

    def make_data_source(self):
        ds = self.data_source.copy()
        ds.set_begin(self)
        return ds

    def pformat(self):
        line_indices = [
            i for i in range(self.line - 2, self.line)
            if i >= 0
        ] or [0]
        lines = self.data_source.data.splitlines()
        return '\n'.join([lines[n] for n in line_indices if lines[n]] + [
            ('-' * (self.column - 1)) + '^'
        ])
