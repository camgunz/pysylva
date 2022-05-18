import typing

from attrs import define

from .. import errors
from ..location import Location
from .type_mapping import Field


@define(eq=False, slots=True)
class DeferredTypeLookup:
    location: Location
    value: str


@define(eq=False, slots=True)
class SelfReferentialMixIn:
    name: str | None
    fields: typing.List[Field] = []

    def resolve_self_references(self):
        from .pointer import BasePointerType

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

    # We have to do this for anything that's SelfReferential.
    # we don't, because this is the only LLVM type that can have
    # self-references.
    def define_llvm_type(self, module):
        # [TODO] Actually write
        if self.name is None:
            for f in self.fields:
                if not isinstance(f.type, BasePointerType):
                    continue
                if not f.type.referenced_type == self:
                    continue
                raise Exception('Cannot have self-referential struct literals')
            struct = ir.LiteralStructType([
                f.type.llvm_type for f in self.fields
            ])
        else:
            struct = self._module.get_identified_type(self.name)
            fields = []
            for f in self.fields:
                if not isinstance(f.type, BasePointerType):
                    fields.append(f.type.llvm_type)
                elif not f.type.referenced_type == self:
                    fields.append(f.type.llvm_type)
                else:
                    fields.append(ir.PointerType(struct))
            struct.set_body(*fields)

        self.llvm_type = struct

        return struct
