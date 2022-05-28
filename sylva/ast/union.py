from .. import errors, utils
from .sylva_type import SylvaType


class BaseUnionType(SylvaType):

    def __init__(self, location, fields):
        SylvaType.__init__(self, location)

        dupes = utils.get_dupes(f.name for f in fields)
        if dupes:
            raise errors.DuplicateFields(self, dupes)

        self.fields = fields

    def get_largest_field(self):
        largest_field = self.fields[0]
        for f in self.fields[1:]:
            if f.get_size() > largest_field.get_size():
                largest_field = f
        return largest_field.llvm_type

    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f
