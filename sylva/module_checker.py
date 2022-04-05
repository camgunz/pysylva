from collections import defaultdict

from . import errors, types


def get_dupes(strs):
    counts = defaultdict(lambda: 0)
    for s in strs:
        counts[s] += 1
    return [s for s, count in counts.items() if count > 1]


class ModuleChecker:

    def __init__(self, module):
        self.module = module
        self.errors = []

    def resolve_self_references(self, obj, name, fields):
        for field_type in fields.values():
            if not isinstance(field_type, types.BasePointer):
                continue
            if not isinstance(field_type.referenced_type,
                              types.DeferredTypeLookup):
                continue
            pointer = field_type
            deferred_lookup = pointer.referenced_type
            if deferred_lookup.value == name:
                pointer.referenced_type = obj
            else:
                self.errors.append(
                    errors.UndefinedSymbol(
                        deferred_lookup.location, deferred_lookup.value
                    )
                )

    def check_cfunction(self, name, cfunction):
        dupes = get_dupes(cfunction.parameters.keys())
        if dupes:
            self.errors.append(
                errors.DuplicateCFunctionParameters(name, cfunction, dupes)
            )

        self.resolve_self_references(cfunction, name, cfunction.fields)

    def check_cstruct(self, name, cstruct):
        dupes = get_dupes(cstruct.fields.keys())
        if dupes:
            self.errors.append(
                errors.DuplicateCStructFields(name, cstruct, dupes)
            )

        self.resolve_self_references(cstruct, name, cstruct.fields)

    def check_cunion(self, name, cunion):
        dupes = get_dupes(cunion.fields.keys())
        if dupes:
            self.errors.append(
                errors.DuplicateCStructFields(name, cunion, dupes)
            )

        self.resolve_self_references(cunion, name, cunion.fields)

    def check_function(self, name, function):
        dupes = get_dupes(function.parameters.keys())
        if dupes:
            self.errors.append(
                errors.DuplicateCFunctionParameters(name, function, dupes)
            )

        self.resolve_self_references(function, name, function.fields)

    def check_struct(self, name, struct):
        dupes = get_dupes(struct.fields.keys())
        if dupes:
            self.errors.append(
                errors.DuplicateCStructFields(name, struct, dupes)
            )

        self.resolve_self_references(struct, name, struct.fields)

    def check(self):
        for name, obj in self.module.vars.items():
            if isinstance(obj, types.CStruct):
                self.check_cstruct(name, obj)
