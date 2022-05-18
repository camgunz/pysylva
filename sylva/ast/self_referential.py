import typing

from attrs import define

from . import errors, type_mapping
from .location import Location


@define(eq=False, slots=True)
class DeferredTypeLookup:
    location: Location
    value: str


@define(eq=False, slots=True)
class SelfReferentialMixIn:
    name: str | None
    fields: typing.List[type_mapping.Field] = []

    def resolve_self_references(self):
        from .ast import BasePointerType

        missing_field_errors = []

        for field in self.fields:
            if not isinstance(field.type, BasePointerType):
                continue
            if not isinstance(field.type.referenced_type, DeferredTypeLookup):
                continue
            pointer = field.type
            deferred_lookup = pointer.referenced_type
            if self.name is not None and deferred_lookup.value == self.name:
                pointer.referenced_type = self
            else:
                missing_field_errors.append(
                    errors.UndefinedSymbol(
                        deferred_lookup.location, deferred_lookup.value
                    )
                )

        return missing_field_errors
