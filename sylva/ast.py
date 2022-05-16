# pylint: disable=too-many-lines

import ctypes
import enum
import typing

from functools import cache, cached_property

from attrs import define, field
from llvmlite import ir # type: ignore

# pylint: disable=unused-import
from . import debug, errors, utils
from .location import Location
from .operator import Operator


_SIZE_SIZE = ctypes.sizeof(ctypes.c_size_t) * 8


@define(eq=False, slots=True)
class ASTNode:
    location: Location


@define(eq=False, slots=True)
class Decl(ASTNode):
    name: str


@define(eq=False, slots=True)
class ModuleDecl(Decl):
    pass


@define(eq=False, slots=True)
class RequirementDecl(Decl):
    pass


@define(eq=False, slots=True)
class SylvaType(ASTNode):
    implementations: typing.List = []

    # pylint: disable=no-self-use
    def check(self):
        return []

    def mangle(self):
        raise NotImplementedError()

    def add_implementation(self, implementation):
        self.implementations.append(implementation)


@define(eq=False, slots=True)
class Lookupable:
    pass


@define(eq=False, slots=True)
class Dotable(Lookupable):

    def get_attribute(self, location, name):
        pass

    def lookup_attribute(self, location, name, module):
        raise NotImplementedError()


@define(eq=False, slots=True)
class Indexable:

    def get_slot(self, location, index):
        pass

    def index_slot(self, location, index):
        raise NotImplementedError()


@define(eq=False, slots=True)
class DotIndexable(Dotable, Indexable):
    pass


@define(eq=False, slots=True)
class Reflectable(Lookupable):

    def get_reflection_attribute_type(self, location, name, module):
        pass

    def reflect_attribute(self, location, name, module):
        raise NotImplementedError()


@define(eq=False, slots=True)
class MetaSylvaType(SylvaType):

    @property
    def names(self):
        raise NotImplementedError()

    @property
    def types(self):
        raise NotImplementedError()

    def check(self):
        type_errors = super().check()

        dupes = utils.get_dupes(self.names)
        if dupes:
            type_errors.append(errors.DuplicateFields(self, dupes))

        return type_errors

    def resolve_self_references(self, name):
        missing_field_errors = []

        for field_type in self.types:
            if not isinstance(field_type, BasePointerType):
                continue
            if not isinstance(field_type.referenced_type, DeferredTypeLookup):
                continue
            pointer = field_type
            deferred_lookup = pointer.referenced_type
            if deferred_lookup.value == name:
                pointer.referenced_type = self
            else:
                missing_field_errors.append(
                    errors.UndefinedSymbol(
                        deferred_lookup.location, deferred_lookup.value
                    )
                )

        return missing_field_errors


@define(eq=False, slots=True)
class SylvaLLVMType(SylvaType):

    @cache
    def make_constant(self, module, value):
        return self.get_llvm_type(module)(value)

    @cache
    def get_alignment(self, module):
        return self.get_llvm_type(module).get_abi_alignment(module.target.data)

    @cache
    def get_size(self, module):
        return self.get_llvm_type(module).get_abi_size(module.target.data)

    @cache
    def get_pointer(self, module):
        return self.get_llvm_type(module).as_pointer()

    @cache
    def get_llvm_type(self, module):
        raise NotImplementedError()


@define(eq=False, slots=True)
class BaseTypeMapping(ASTNode):
    name: str
    type: SylvaLLVMType
    index: int | None = None

    @property
    def handle(self):
        return self.index if self.index is not None else self.name

    @cache
    def get_alignment(self, module):
        return self.type.get_llvm_type(module).get_abi_alignment(
            module.target.data
        )

    @cache
    def get_size(self, module):
        return self.type.get_llvm_type(module).get_abi_size(module.target.data)

    @cache
    def get_pointer(self, module):
        return self.type.get_llvm_type(module).as_pointer()

    @cache
    def get_llvm_type(self, module):
        return self.type.get_llvm_type(module)


@define(eq=False, slots=True)
class Parameter(BaseTypeMapping):
    pass


@define(eq=False, slots=True)
class Attribute(BaseTypeMapping):
    pass


@define(eq=False, slots=True)
class Field(BaseTypeMapping):
    pass


@define(eq=False, slots=True)
class SylvaParamType(SylvaType):
    monomorphizations: typing.List = []

    def check(self):
        type_errors = super().check()

        for mm in self.monomorphizations:
            type_errors.extend(mm.check())

        return type_errors

    @property
    def is_polymorphic(self):
        return len(self.monomorphizations) > 1

    @cache
    def get_llvm_types(self, module):
        raise NotImplementedError()


@define(eq=False, slots=True)
class MetaSylvaLLVMType(MetaSylvaType, SylvaLLVMType):
    pass


@define(eq=False, slots=True)
class ScalarType(SylvaLLVMType):
    pass


@define(eq=False, slots=True)
class BooleanType(ScalarType):

    @cache
    def mangle(self):
        return '1b'

    @cache
    def get_value_expr(self, location):
        return BooleanExpr(location=location, type=self)

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(8)


@define(eq=False, slots=True)
class RuneType(ScalarType):

    @cache
    def mangle(self):
        return '1r'

    @cache
    def get_value_expr(self, location):
        return RuneExpr(location=location, type=self)

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(32)


@define(eq=False, slots=True)
class NumericType(ScalarType):
    pass


@define(eq=False, slots=True)
class SizedNumericType(NumericType):
    bits: int
    implementations: typing.List = []


@define(eq=False, slots=True)
class ComplexType(SizedNumericType):

    @cache
    def mangle(self):
        base = f'c{self.bits}'
        return f'{len(base)}{base}'

    @cache
    def get_value_expr(self, location):
        return ComplexExpr(location=location, type=self)

    @cache
    def get_llvm_type(self, module):
        if self.bits == 8:
            return ir.HalfType()
        if self.bits == 16:
            return ir.FloatType()
        if self.bits == 32:
            return ir.DoubleType()
        # [NOTE] llvmlite won't do float types > 64 bits
        if self.bits == 64:
            return ir.DoubleType()
        if self.bits == 128:
            return ir.DoubleType()


@define(eq=False, slots=True)
class FloatType(SizedNumericType):

    @cache
    def mangle(self):
        base = f'f{self.bits}'
        return f'{len(base)}{base}'

    @cache
    def get_value_expr(self, location):
        return FloatExpr(location=location, type=self)

    @cache
    def get_llvm_type(self, module):
        # [NOTE] llvmlite won't do float types < 16 bits
        if self.bits == 8:
            return ir.HalfType()
        if self.bits == 16:
            return ir.HalfType()
        if self.bits == 32:
            return ir.FloatType()
        if self.bits == 64:
            return ir.DoubleType()
        # [NOTE] llvmlite won't do float types > 64 bits
        if self.bits == 128:
            return ir.DoubleType()


@define(eq=False, slots=True)
class IntegerType(SizedNumericType):
    signed: bool
    implementations: typing.List = []

    @cache
    def mangle(self):
        prefix = 'i' if self.signed else 'u'
        base = f'{prefix}{self.bits}'
        return f'{len(base)}{base}'

    @classmethod
    def SmallestThatHolds(cls, x):
        return cls(Location.Generate(), utils.smallest_uint(x), signed=False)

    @classmethod
    def Platform(cls, signed):
        return cls(Location.Generate(), bits=_SIZE_SIZE, signed=signed)

    @cache
    def get_value_expr(self, location):
        return IntegerExpr(location=location, type=self)

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(self.bits)


@define(eq=False, slots=True)
class MonoArrayType(SylvaLLVMType, Reflectable):
    element_type: SylvaType
    element_count: int = field()
    implementations: typing.List = []

    @cache
    def mangle(self):
        base = f'a{self.element_type.mangle()}{self.element_count}'
        return f'{len(base)}{base}'

    # pylint: disable=unused-argument
    @element_count.validator
    def check_element_count(self, attribute, value):
        if value is not None and value <= 0:
            raise errors.EmptyArray(self.location)

    @cache
    def get_llvm_type(self, module):
        return ir.ArrayType(
            self.element_type.get_llvm_type(module), self.element_count
        )

    # pylint: disable=no-self-use
    @cache
    def get_reflection_attribute_type(self, location, name, module):
        if name == 'name':
            return StrType
        if name == 'size':
            return IntegerType
        if name == 'count':
            return IntegerType
        if name == 'element_type':
            return SylvaType
        if name == 'indices':
            return RangeType

    def reflect_attribute(self, location, name, module):
        # [FIXME] These need to be Sylva expressions that evaluate to LLVM
        #         values
        if name == 'name':
            return 'array'
        if name == 'size':
            return self.element_count * self.element_type.size # [TODO]
        if name == 'count':
            return self.element_count
        if name == 'element_type':
            return self.element_type
        if name == 'indices':
            return range(0, self.element_count + 1)


# Here, we want some way of saying "this type sort of exists without an
# element_count, but in most contexts it has to have one"
@define(eq=False, slots=True)
class ArrayType(SylvaParamType):
    monomorphizations: typing.List[MonoArrayType] = []

    @classmethod
    def Def(cls, location, element_type, element_count):
        return cls(
            location=location,
            monomorphizations=[
                MonoArrayType(
                    location=location,
                    element_type=element_type,
                    element_count=element_count
                )
            ]
        )

    def add_monomorphization(self, location, element_type, element_count):
        index = len(self.monomorphizations)
        mat = MonoArrayType(
            location=location,
            element_type=element_type,
            element_count=element_count
        )
        self.monomorphizations.append(mat)
        return index


@define(eq=False, slots=True)
class MonoDynarrayType(SylvaLLVMType, Reflectable):
    element_type: SylvaType
    implementations: typing.List = []

    @cache
    def mangle(self):
        base = f'da{self.element_type.mangle()}'
        return f'{len(base)}{base}'

    @cache
    def get_llvm_type(self, module):
        # yapf: disable
        return ir.LiteralStructType([
            Builtins.UINT.value.get_llvm_type(module),           # cap
            Builtins.UINT.value.get_llvm_type(module),           # len
            self.element_type.get_llvm_type(module).as_pointer() # data
        ])

    def lookup_attribute(self, location, name, module):
        raise NotImplementedError()

    # pylint: disable=no-self-use
    @cache
    def get_reflection_attribute_type(self, location, name, module):
        if name == 'name':
            return StrType
        if name == 'size':
            return IntegerType
        if name == 'element_type':
            return self.element_type.type

    def reflect_attribute(self, location, name, module):
        # [FIXME] These need to be Sylva expressions that evaluate to LLVM
        #         values
        if name == 'name':
            return 'dynarray'
        if name == 'size':
            return self.get_size(module)
        if name == 'element_type':
            return self.element_type.get_llvm_type(module)


@define(eq=False, slots=True)
class DynarrayType(SylvaParamType):
    monomorphizations: typing.List[MonoDynarrayType]
    implementations: typing.List = []

    @classmethod
    def Def(cls, location, element_type):
        return cls(
            location=location,
            monomorphizations=[
                MonoDynarrayType(
                    location=location,
                    element_type=element_type,
                )
            ]
        )

    def add_monomorphization(self, location, element_type):
        index = len(self.monomorphizations)
        mdt = MonoDynarrayType(
            location=location,
            element_type=element_type,
        )
        self.monomorphizations.append(mdt)
        return index


@define(eq=False, slots=True)
class StrType(MonoArrayType):
    value: bytearray
    element_type: IntegerType = Builtins.I8.value
    implementations: typing.List = []

    def mangle(self):
        base = f'str{self.element_type.mangle()}{self.element_count}'
        return f'{len(base)}{base}'

    @classmethod
    def FromValue(cls, location, value):
        return cls(location=location, element_count=len(value), value=value)

    @cache
    def get_value_expr(self, location):
        return StrExpr(
            location=location, type=self, value=self.value
        )


@define(eq=False, slots=True)
class StringType(SylvaLLVMType, Dotable, Reflectable):

    def mangle(self):
        return '6string'

    # [FIXME] I think this is wrong; these should be dynarrays?
    def get_value_expr(self, location):
        return StringExpr(location=location, type=self)

    def get_llvm_type(self, module):
        u8 = IntegerType(Location.Generate(), 8, signed=False)
        return DynarrayType(element_type=u8).get_llvm_type(module)

    @cache
    def get_attribute(self, location, name):
        if name == 'get_length':
            return Attribute(
                location=Location.Generate(),
                name='get_length',
                type=FunctionType.Def(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=Builtins.UINT.value
                )
            )

    @cache
    def get_reflection_attribute_type(self, location, name, module):
        # pylint: disable=consider-using-in
        if name == 'type':
            return self # ?
        if name == 'bytes':
            # [FIXME] Make this a shared reference to a dynarray
            return ArrayType(
                Location.Generate(),
                element_type=IntegerType(Location.Generate(), 8, signed=False),
                element_count=1
            )


@define(eq=False, slots=True)
class MonoFunctionType(MetaSylvaLLVMType):
    parameters: typing.List[Parameter]
    return_type: SylvaType
    llvm_value: None | ir.Function = None
    implementations: typing.List = []

    def mangle(self):
        params = ''.join(p.type.mangle() for p in self.parameters)
        base = f'fn{params}{self.return_type.mangle()}'
        return f'{len(base)}{base}'

    @property
    def names(self):
        return [p.name for p in self.parameters]

    @property
    def types(self):
        return [p.type for p in self.parameters]

    @cache
    def get_llvm_type(self, module):
        return ir.FunctionType( # yapf: disable
            (
                self.return_type.get_llvm_type(module)
                if self.return_type else ir.VoidType()
            ),
            [p.type.get_llvm_type(module) for p in self.parameters]
        )


@define(eq=False, slots=True)
class FunctionType(SylvaParamType):
    monomorphizations: typing.List[MonoFunctionType] = []

    @classmethod
    def Def(cls, location, parameters, return_type):
        return cls(
            location=location,
            monomorphizations=[
                MonoFunctionType(location, parameters, return_type)
            ]
        )

    def resolve_self_references(self, name):
        pass # [FIXME] This should run on structs etc., not functions

    def add_monomorphization(self, mono_function_type):
        index = len(self.monomorphizations)
        self.monomorphizations.append(mono_function_type)
        return index


@define(eq=False, slots=True)
class RangeType(MetaSylvaLLVMType):
    type: NumericType
    min: int
    max: int
    implementations: typing.List = []

    def mangle(self):
        return self.type.mangle()

    @property
    def names(self):
        return []

    @property
    def types(self):
        return [self.type]

    @cache
    def get_llvm_type(self, module):
        return self.type.type


@define(eq=False, slots=True)
class BaseStructType(MetaSylvaLLVMType, Dotable):
    name: str | None
    fields: typing.List[Field]
    implementations: typing.List = []

    # self._size = 0
    # self._alignment = 1
    # self._offsets = {}
    # for name, type in self.fields:
    #     self._size = utils.round_up_to_multiple(
    #       self._size, type.alignment
    #     )
    #     self._alignment = max(self._alignment, type.alignment)
    #     self._offsets[name] = self._size
    #     self._size += type.size
    # self._size = utils.round_up_to_multiple(self._size, self._alignment)

    @property
    def names(self):
        return [f.name for f in self.fields]

    @property
    def types(self):
        return [f.type for f in self.fields]

    # pylint: disable=unused-argument
    @cache
    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f

    @cache
    def get_llvm_type(self, module):
        if self.name is None:
            for f in self.fields:
                if not isinstance(f.type, BasePointerType):
                    continue
                if not f.type.referenced_type == self:
                    continue
                raise Exception('Cannot have self-referential struct literals')
            return ir.LiteralStructType([
                f.type.get_llvm_type(module) for f in self.fields
            ])

        struct = module.get_identified_type(self.name)
        fields = []
        for f in self.fields:
            if not isinstance(f.type, BasePointerType):
                fields.append(f.type.get_llvm_type(module))
            elif not f.type.referenced_type == self:
                fields.append(f.type.get_llvm_type(module))
            else:
                fields.append(ir.PointerType(struct))
        struct.set_body(*fields)

        return struct


@define(eq=False, slots=True)
class MonoStructType(BaseStructType):
    pass


@define(eq=False, slots=True)
class StructType(SylvaParamType):
    name: str | None
    monomorphizations: typing.List[MonoStructType] = []
    implementations: typing.List = []

    @classmethod
    def Def(cls, location, name, fields):
        return cls(
            location=location,
            name=name,
            monomorphizations=[
                MonoStructType(location=location, name=name, field=fields)
            ]
        )

    def add_monomorphization(self, fields):
        index = len(self.monomorphizations)
        mst = MonoStructType(name=self.name, fields=fields)
        self.monomorphizations.append(mst)
        return index


@define(eq=False, slots=True)
class BaseUnionType(MetaSylvaLLVMType):
    fields: typing.List[Field] = []

    @property
    def names(self):
        return [f.name for f in self.fields]

    @property
    def types(self):
        return [f.type for f in self.fields]

    @cache
    def get_largest_field(self, module):
        largest_field = self.fields[0]
        for f in self.fields[1:]:
            if f.get_size(module) > largest_field.get_size(module):
                largest_field = f
        return largest_field.get_llvm_type(module)

    # pylint: disable=unused-argument
    @cache
    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f


@define(eq=False, slots=True)
class MonoVariantType(BaseUnionType, Dotable):
    name: str
    fields: typing.List[Field] = []
    implementations: typing.List = []

    @property
    def names(self):
        return [f.name for f in self.fields]

    @property
    def types(self):
        return [f.type for f in self.fields]

    # pylint: disable=unused-argument
    @cache
    def get_attribute(self, location, name):
        for f in self.fields:
            if f.name == name:
                return f

    @cache
    def get_llvm_type(self, module):
        tag_bit_width = utils.round_up_to_multiple(len(self.fields), 8)
        return ir.LiteralStructType([
            self.get_largest_field(module), ir.IntType(tag_bit_width)
        ])


@define(eq=False, slots=True)
class VariantType(SylvaParamType):
    name: str
    monomorphizations: typing.List[MonoVariantType] = []
    implementations: typing.List = []


@define(eq=False, slots=True)
class BasePointerType(MetaSylvaLLVMType, Dotable, Reflectable):
    referenced_type: SylvaType
    is_exclusive: bool
    implementations: typing.List = []

    @property
    def names(self):
        return []

    @property
    def types(self):
        return [self.referenced_type]

    @cache
    def get_llvm_type(self, module):
        return ir.PointerType(self.referenced_type.get_llvm_type(module))

    @cache
    def get_attribute(self, location, name):
        if not isinstance(self.referenced_type, Dotable):
            raise errors.ImpossibleLookup(location)
        return self.referenced_type.get_attribute(location, name)

    @cache
    def get_reflection_attribute_type(self, location, name, module):
        return self.referenced_type.get_reflection_attribute_type(
            location, name, module
        )


@define(eq=False, slots=True)
class ReferencePointerType(BasePointerType):
    pass


@define(eq=False, slots=True)
class OwnedPointerType(BasePointerType):
    is_exclusive: bool = True


@define(eq=False, slots=True)
class CPointerType(BasePointerType):
    referenced_type_is_exclusive: bool
    implementations: typing.List = []


@define(eq=False, slots=True)
class ModuleType(SylvaType, Dotable):
    # Module, but we can't because it would be circular
    value: typing.Any
    implementations: typing.List = []

    @cache
    def get_attribute(self, location, name):
        return self.value.get_attribute(location, name)

    @cache
    def lookup_attribute(self, location, name, module):
        return self.value.lookup_attribute(location, name, module)


@define(eq=False, slots=True)
class CBitFieldType(SylvaLLVMType):
    bits: int
    signed: bool
    field_size: int
    implementations: typing.List = []

    @cache
    def get_llvm_type(self, module):
        return ir.IntType(self.bits)


@define(eq=False, slots=True)
class CVoidType(SylvaLLVMType):

    @cache
    def get_llvm_type(self, module):
        # return ir.VoidType()
        raise Exception('Cannot get the LLVM type of CVoid')


@define(eq=False, slots=True)
class CStringType(ScalarType):

    @cache
    def get_llvm_type(self, module):
        return ir.PointerType(ir.IntType(8))


@define(eq=False, slots=True)
class CArrayType(MonoArrayType):
    # [TODO] I think these... are also now Param?
    element_count: int
    implementations: typing.List = []


@define(eq=False, slots=True)
class BaseCFunctionType(MetaSylvaLLVMType):
    parameters: typing.List[Parameter]
    return_type: SylvaType
    implementations: typing.List = []

    @property
    def names(self):
        return [p.name for p in self.parameters]

    @property
    def types(self):
        return [p.type for p in self.parameters]

    @cache
    def get_llvm_type(self, module):
        params = []

        for p in self.parameters:
            params.append(p.type.get_llvm_type(module))

        return ir.FunctionType(
            self.return_type.get_llvm_type(module)
            if self.return_type else ir.VoidType(),
            params
        )


@define(eq=False, slots=True)
class CFunctionType(BaseCFunctionType):
    pass


@define(eq=False, slots=True)
class CFunctionPointerType(BaseCFunctionType):

    def get_llvm_type(self, module):
        return super().get_llvm_type(module).as_pointer()


@define(eq=False, slots=True)
class CBlockFunctionType(BaseCFunctionType):
    pass


@define(eq=False, slots=True)
class CBlockFunctionPointerType(BaseCFunctionType):

    def get_llvm_type(self, module):
        return super().get_llvm_type(module).as_pointer()


@define(eq=False, slots=True)
class CStructType(BaseStructType):
    pass


@define(eq=False, slots=True)
class CUnionType(BaseUnionType):

    @cache
    def get_llvm_type(self, module):
        return ir.LiteralStructType([self.get_largest_field(module)])


@define(eq=False, slots=True)
class Expr(ASTNode, Reflectable):
    type: SylvaType

    # pylint: disable=no-self-use
    @cache
    def get_reflection_attribute_type(self, location, name, module):
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return ArrayType

    def reflect_attribute(self, location, name, module):
        if name == 'type':
            return self.type
        if name == 'bytes':
            pass


@define(eq=False, slots=True)
class LLVMExpr(Expr):

    def emit_llvm_expr(self, module, builder):
        raise NotImplementedError()


@define(eq=False, slots=True)
class ValueExpr(LLVMExpr):
    llvm_value: None | ir.Value

    def emit_llvm_expr(self, module, builder):
        return builder.load(self.llvm_value)


@define(eq=False, slots=True)
class LiteralExpr(LLVMExpr):
    value: typing.Any

    @cache
    def emit_llvm_expr(self, module, builder):
        return self.type.get_llvm_type(module)(self.value)


@define(eq=False, slots=True)
class ScalarExpr(LiteralExpr):
    value: bool | float | int | str


@define(eq=False, slots=True)
class BooleanScalarExpr(ScalarExpr):
    type: BooleanType = BooleanType(Location.Generate())

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value == 'true')

    @cache
    def emit_llvm_expr(self, module, builder):
        return self.type.get_llvm_type(module)(1 if self.value else 0)


@define(eq=False, slots=True)
class BooleanExpr(ValueExpr):
    type: BooleanType = BooleanType(Location.Generate())


@define(eq=False, slots=True)
class RuneScalarExpr(ScalarExpr):
    type: RuneType = RuneType(Location.Generate())

    @classmethod
    def FromRawValue(cls, location, raw_value):
        return cls(location, value=raw_value[1:-1])


@define(eq=False, slots=True)
class RuneExpr(ValueExpr):
    type: RuneType = RuneType(Location.Generate())


@define(eq=False, slots=True)
class NumericScalarExpr(ScalarExpr):
    pass


@define(eq=False, slots=True)
class IntegerScalarExpr(NumericScalarExpr):
    type: IntegerType

    @classmethod
    def Platform(cls, location, signed, value):
        return cls(location, IntegerType(_SIZE_SIZE, signed=signed), value)

    @classmethod
    def SmallestThatHolds(cls, location, value):
        type = IntegerType(size=utils.smallest_uint(value), signed=False)
        return cls(location=location, type=type, value=value)

    @classmethod
    def FromRawValue(cls, location, raw_value):
        if raw_value.startswith('0b') or raw_value.startswith('0B'):
            base = 2
        elif raw_value.startswith('0o') or raw_value.startswith('0O'):
            base = 8
        elif raw_value.startswith('0x') or raw_value.startswith('0X'):
            base = 16
        else:
            base = 10

        if raw_value.endswith('i'):
            signed, size, value = True, None, int(raw_value[:-1], base)
        elif raw_value.endswith('i8'):
            signed, size, value = True, 8, int(raw_value[:-2], base)
        elif raw_value.endswith('i16'):
            signed, size, value = True, 16, int(raw_value[:-3], base)
        elif raw_value.endswith('i32'):
            signed, size, value = True, 32, int(raw_value[:-3], base)
        elif raw_value.endswith('i64'):
            signed, size, value = True, 64, int(raw_value[:-3], base)
        elif raw_value.endswith('i128'):
            signed, size, value = True, 128, int(raw_value[:-4], base)
        elif raw_value.endswith('u'):
            signed, size, value = False, None, int(raw_value[:-1], base)
        elif raw_value.endswith('u8'):
            signed, size, value = False, 8, int(raw_value[:-2], base)
        elif raw_value.endswith('u16'):
            signed, size, value = False, 16, int(raw_value[:-3], base)
        elif raw_value.endswith('u32'):
            signed, size, value = False, 32, int(raw_value[:-3], base)
        elif raw_value.endswith('u64'):
            signed, size, value = False, 64, int(raw_value[:-3], base)
        elif raw_value.endswith('u128'):
            signed, size, value = False, 128, int(raw_value[:-4], base)
        else: # [NOTE] Warn here?
            signed, size = False, None

        return cls(
            location=location,
            type=IntegerType(
                location=location, bits=size or _SIZE_SIZE, signed=signed
            ),
            value=value
        )

    @property
    def signed(self):
        return self.type.signed

    @property
    def size(self):
        return self.type.bits


@define(eq=False, slots=True)
class IntegerExpr(ValueExpr):
    type: IntegerType


@define(eq=False, slots=True)
class FloatScalarExpr(NumericScalarExpr):
    type: FloatType

    @classmethod
    def FromRawValue(cls, location, raw_value):
        if raw_value.endswith('f16'):
            return cls(location, FloatType(16), float(raw_value[:-3]))
        if raw_value.endswith('f32'):
            return cls(location, FloatType(32), float(raw_value[:-3]))
        if raw_value.endswith('f64'):
            return cls(location, FloatType(64), float(raw_value[:-3]))
        if raw_value.endswith('f128'):
            return cls(location, FloatType(128), float(raw_value[:-4]))
        raise Exception(f'Malformed float value {raw_value}')

    @property
    def size(self):
        return self.type.bits


@define(eq=False, slots=True)
class FloatExpr(ValueExpr):
    type: FloatType


@define(eq=False, slots=True)
class ComplexScalarExpr(NumericScalarExpr):
    type: ComplexType

    @classmethod
    def FromRawValue(cls, location, raw_value):
        if raw_value.endswith('f16'):
            return cls(location, ComplexType(16), complex(raw_value[:-3]))
        if raw_value.endswith('f32'):
            return cls(location, ComplexType(32), complex(raw_value[:-3]))
        if raw_value.endswith('f64'):
            return cls(location, ComplexType(64), complex(raw_value[:-3]))
        if raw_value.endswith('f128'):
            return cls(location, ComplexType(128), complex(raw_value[:-4]))
        raise Exception(f'Malformed complex value {raw_value}')

    @property
    def size(self):
        return self.type.bits


@define(eq=False, slots=True)
class ComplexExpr(ValueExpr):
    type: ComplexType


@define(eq=False, slots=True)
class ArrayLiteralExpr(LiteralExpr):
    type: ArrayType

    @classmethod
    def FromRawValue(cls, location, element_type, raw_value):
        return cls(location, element_type, len(raw_value), raw_value)


@define(eq=False, slots=True)
class ArrayExpr(ValueExpr, Reflectable):
    type: ArrayType

    def get_reflection_attribute_type(self, location, name, module):
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return ReferencePointerType(
                referenced_type=ArrayType(
                    Location.Generate(),
                    element_type=IntegerType(
                        Location.Generate(), 8, signed=False
                    ),
                    element_count=self.type.get_size(module)
                )
            )

    def reflect_attribute(self, location, name, module):
        if name == 'type':
            # [FIXME]
            return SylvaType
        if name == 'bytes':
            # [NOTE] Just overriding the type here _probably_ works, but only
            #        implicitly. It would be better if we had explicit support
            #        throughout.
            return ReferencePointerExpr(
                location=Location.Generate(),
                type=ReferencePointerType(
                    referenced_type=ArrayType(
                        Location.Generate(),
                        element_type=IntegerType(
                            Location.Generate(), 8, signed=False
                        ),
                        element_count=self.type.get_size(module)
                    )
                ),
                expr=self
            )


@define(eq=False, slots=True)
class DynarrayLiteralExpr(LiteralExpr):
    type: DynarrayType

    @classmethod
    def FromRawValue(cls, location, element_type, raw_value):
        # [FIXME] This involves heap allocation, and is therefore a little
        #         tricker than this
        return cls(location, element_type, len(raw_value), raw_value)


@define(eq=False, slots=True)
class DynarrayExpr(ValueExpr, Reflectable):
    type: DynarrayType

    # pylint: disable=no-self-use,unused-argument
    @cache
    def get_attribute(self, location, name):
        if name == 'get_length':
            return Attribute(
                location=Location.Generate(),
                name='get_length',
                type=FunctionType.Def(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=Builtins.UINT.value
                )
            )

    def lookup_attribute(self, location, name, module):
        raise NotImplementedError()

    def get_reflection_attribute_type(self, location, name, module):
        if name == 'type':
            return SylvaType
        if name == 'bytes':
            return ReferencePointerType(
                referenced_type=ArrayType(
                    Location.Generate(),
                    element_type=IntegerType(
                        Location.Generate(), 8, signed=False
                    ),
                    element_count=self.type.get_size(module)
                )
            )

    def reflect_attribute(self, location, name, module):
        if name == 'type':
            # [FIXME]
            return SylvaType
        if name == 'bytes':
            # [NOTE] Just overriding the type here _probably_ works, but only
            #        implicitly. It would be better if we had explicit support
            #        throughout.
            return ReferencePointerExpr(
                location=Location.Generate(),
                type=ReferencePointerType(
                    referenced_type=ArrayType(
                        Location.Generate(),
                        element_type=IntegerType(
                            Location.Generate(), 8, signed=False
                        ),
                        element_count=self.type.get_size(module)
                    )
                ),
                expr=self
            )


@define(eq=False, slots=True)
class StrExpr(LiteralExpr, Dotable):
    type: StrType

    # pylint: disable=arguments-differ
    @classmethod
    def FromRawValue(cls, location, raw_value):
        # [NOTE] I suppose this is where we'd configure internal string
        #        encoding.
        encoded_data = bytearray(raw_value[1:-1], encoding='utf-8')
        return cls(
            location,
            type=StrType.FromValue(location, encoded_data),
            value=encoded_data
        )

    @cache
    def get_attribute(self, location, name):
        if name == 'get_length':
            return Attribute(
                name='get_length',
                type=FunctionType(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=Builtins.UINT.value
                )
            )

    @cache
    def lookup_attribute(self, location, name, module):
        # Actually... where does this live? We can't just return an uncompiled
        # function. This is... actually a LookupExpr to a built-in impl
        # somewhere.
        if name == 'get_length':
            return Function(
                name='get_length',
                location=Location.Generate(),
                type=self.get_attribute(location, 'get_length')[1],
                code=[
                    Return(
                        location=Location.Generate(),
                        expr=IntegerScalarExpr.Platform(
                            location=location,
                            signed=False,
                            value=len(self.value)
                        )
                    )
                ]
            )

    @cache
    def get_reflection_attribute_type(self, location, name, module):
        # pylint: disable=consider-using-in
        if name == 'size' or name == 'count':
            return self.type.get_reflection_attribute_type(
                location, name, module
            )

    @cache
    def reflect_attribute(self, location, name, module):
        if name == 'size':
            return len(self.value)
        if name == 'count':
            return len(self.value.decode('utf-8'))


"""
# @define(eq=False, slots=True)
# class StringExpr(ArrayExpr, Dotable):
#     type: StringType
#
#     @cache
#     def get_attribute(self, location, name):
#         if name == 'get_length':
#             return Attribute(
#                 name='get_length',
#                 type=FunctionType(
#                     location=Location.Generate(),
#                     parameters=[],
#                     return_type=Builtins.UINT.value
#                 )
#             )
#
#     @cache
#     def lookup_attribute(self, location, name, module):
#         type=self.get_attribute(location, 'get_length')[1],
#         if name == 'get_length':
#             return Function(
#                 location=Location.Generate(),
#                 type=type,
#                 code=[
#                     Return(
#                         location=Location.Generate(),
#                         expr=AttributeLookupExpr(
#
#                             signed=False,
#                             value=len(self.value)
#                         )
#                     )
#                 ]
#             )
#
#     def get_reflection_attribute_type(self, location, name, module):
#         # pylint: disable=consider-using-in
#         if name == 'size' or name == 'count':
#             return self.type.get_reflection_attribute_type(location, name, module)
#
#     def reflect_attribute(self, location, name, module):
#         pass
"""


@define(eq=False, slots=True)
class BaseLookupExpr(Expr, Dotable, Reflectable):

    def get_attribute(self, location, name):
        return self.type.get_attribute(location, name)

    def get_reflection_attribute_type(self, location, name, module):
        return self.type.get_reflection_attribute_type(location, name, module)


@define(eq=False, slots=True)
class LookupExpr(BaseLookupExpr):
    name: str


@define(eq=False, slots=True)
class AttributeLookupExpr(BaseLookupExpr):
    expr: Expr
    attribute: str | int
    reflection: bool


@define(eq=False, slots=True)
class FieldIndexLookupExpr(Expr):
    expr: Expr
    index: int

    # def emit(self, builder, name=None):
    #     indices = [self.index]
    #     expr = self.expr # struct, cstruct... array?
    #     while isinstance(expr, FieldIndexLookupExpr):
    #         expr = expr.expr
    #         indices.insert(0, expr.index)
    #     return builder.gep(
    #         self.expr.eval(scope), indices, inbounds=True, name=name
    #     )


@define(eq=False, slots=True)
class ReflectionLookupExpr(Expr):
    expr: Expr
    name: str


@define(eq=False, slots=True)
class FunctionExpr(ValueExpr):
    type: FunctionType


@define(eq=False, slots=True)
class CallExpr(LLVMExpr):
    function: Expr
    arguments: typing.List[Expr]
    monomorphization_index: int | None = None
    llvm_function: ir.Function | None = None
    llvm_arguments: typing.List[ir.Value] | None = None

    @classmethod
    def Def(cls, location, type, function, arguments,
            monomorphization_index=0):
        return cls(
            location=location,
            type=type,
            function=function,
            arguments=arguments,
            monomorphization_index=monomorphization_index
        )

    @cache
    def emit_llvm_expr(self, module, builder):
        return builder.call(
            self.llvm_function, self.llvm_arguments, cconv='fastcc'
        )


@define(eq=False, slots=True)
class IndexExpr(Expr):
    indexable: Expr
    index: Expr


@define(eq=False, slots=True)
class UnaryExpr(Expr):
    operator: str = field()
    expr: Expr

    # pylint: disable=unused-argument
    @operator.validator
    def check_value(self, attribute, value):
        if value == '+' and not isinstance(self.expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if value == '-' and not isinstance(self.expr.type, NumericType):
            raise errors.InvalidExpressionType(self.location, 'number')
        if value == '~' and not isinstance(self.expr.type, IntegerType):
            raise errors.InvalidExpressionType(self.location, 'integer')
        if value == '!' and not isinstance(self.expr.type, BooleanType):
            raise errors.InvalidExpressionType(self.location, 'bool')


@define(eq=False, slots=True)
class BinaryExpr(Expr):
    operator: Operator
    lhs: Expr
    rhs: Expr


@define(eq=False, slots=True)
class BasePointerExpr(ValueExpr):

    @property
    def referenced_type(self):
        return self.type.referenced_type

    @property
    def is_exclusive(self):
        return self.type.is_exclusive


@define(eq=False, slots=True)
class ReferencePointerExpr(BasePointerExpr):
    type: ReferencePointerType
    value: Expr


@define(eq=False, slots=True)
class MovePointerExpr(BasePointerExpr):
    type: OwnedPointerType
    value: Expr


@define(eq=False, slots=True)
class OwnedPointerExpr(BasePointerExpr):
    type: OwnedPointerType


@define(eq=False, slots=True)
class CPointerCastExpr(BasePointerExpr):

    """
    "Cast" is a misnomer here because while this casts other pointer
    types, it takes a (c) pointer to non-pointer types.
    """

    type: CPointerType
    expr: Expr


@define(eq=False, slots=True)
class CVoidCastExpr(Expr):
    expr: Expr
    type: IntegerType = Builtins.I8.value


@define(eq=False, slots=True)
class Stmt(ASTNode):
    pass


@define(eq=False, slots=True)
class LetStmt(Stmt):
    name: str
    expr: Expr


@define(eq=False, slots=True)
class StmtBlock(Stmt):
    code: list[Expr | Stmt]


@define(eq=False, slots=True)
class Break(Stmt):
    pass


@define(eq=False, slots=True)
class Continue(Stmt):
    pass


@define(eq=False, slots=True)
class Return(Stmt):
    expr: Expr


@define(eq=False, slots=True)
class If(StmtBlock):
    conditional_expr: Expr
    else_code: list[Expr | Stmt]


@define(eq=False, slots=True)
class Loop(StmtBlock):
    pass


@define(eq=False, slots=True)
class While(StmtBlock):
    conditional_expr: Expr


@define(eq=False, slots=True)
class Alias(ASTNode):
    name: str
    value: str | SylvaType = field()

    # pylint: disable=unused-argument
    @value.validator
    def check_value(self, attribute, value):
        if isinstance(value, str) and value == self.name:
            raise errors.RedundantAlias(self.location, self.name)


@define(eq=False, slots=True)
class Def(ASTNode):
    name: str
    type: SylvaType


# @define(eq=False, slots=True)
# class LLVMParamDef(Def):
#
#     def set_llvm_value(self, index, llvm_value):
#         raise NotImplementedError()


@define(eq=False, slots=True)
class Const(Def):
    value: LiteralExpr
    llvm_value: None | ir.Value = None

    def get_llvm_value(self, module):
        return self.value.get_llvm_value(module)


@define(eq=False, slots=True)
class Function(Def):
    type: FunctionType
    code: list[Expr | Stmt]

    def get_llvm_value(self, index):
        return self.type.monomorphizations[index].llvm_value

    def set_llvm_value(self, index, llvm_value):
        self.type.monomorphizations[index].llvm_value = llvm_value


@define(eq=False, slots=True)
class CFunction(Def):
    type: CFunctionType
    llvm_value: None | ir.Function = None


@define(eq=False, slots=True)
class TypeDef(Def):

    def get_llvm_type(self, module):
        return self.type.get_llvm_type(module)


@define(eq=False, slots=True)
class ParamTypeDef(TypeDef):

    # pylint: disable=arguments-differ
    def get_llvm_type(self, module, index):
        return self.type.monomorphizations[index].get_llvm_type(module)


@define(eq=False, slots=True)
class CArray(TypeDef):
    pass


@define(eq=False, slots=True)
class Struct(TypeDef, DotIndexable):
    llvm_value: None | ir.Value = None

    def get_attribute(self, location, name):
        f = self.type.get_attribute(location, name)
        if not f:
            raise errors.NoSuchField(location, name)
        return f

    def lookup_attribute(self, location, name, module):
        f = self.get_attribute(location, name)
        if not f:
            raise errors.NoSuchField(location, name)
        return GetElementPointerExpr(
            location, type=f.type, obj=self, index=f.index, name=name
        )

    def get_slot(self, location, index):
        if index >= len(self.type.fields):
            raise errors.IndexOutOfBounds(location)
        return self.type.fields[index]

    def index_slot(self, location, index):
        return self.get_slot(location, index).get_value_expr(location=location)


@define(eq=False, slots=True)
class CStruct(TypeDef, DotIndexable):
    llvm_value: None | ir.Value = None

    def get_attribute(self, location, name):
        f = self.type.get_attribute(location, name)
        if not f:
            raise errors.NoSuchField(location, name)
        return f

    def lookup_attribute(self, location, name, module):
        f = self.get_attribute(location, name)
        if not f:
            raise errors.NoSuchField(location, name)
        return GetElementPointerExpr(
            location, type=f.type, obj=self, index=f.index, name=name
        )

    def get_slot(self, location, index):
        if index >= len(self.type.fields):
            raise errors.IndexOutOfBounds(location)
        return self.type.fields[index]

    def index_slot(self, location, index):
        return self.get_slot(location, index).get_value_expr(location=location)


@define(eq=False, slots=True)
class DeferredTypeLookup(ASTNode):
    value: str


@define(eq=False, slots=True)
class InterfaceType(SylvaType, Dotable):
    functions: typing.List[Attribute]
    implementations: typing.List = []

    def check(self):
        type_errors = super().check()

        dupes = utils.get_dupes(x.name for x in self.functions)
        if dupes:
            type_errors.append(errors.DuplicateFields(self, dupes))

        return type_errors

    # pylint: disable=unused-argument
    @cache
    def get_attribute(self, location, name):
        for func_attr in self.functions:
            if func_attr.name == name:
                return func_attr.type

    def add_implementation(self, implementation):
        self.implementations.append(implementation)


@define(eq=False, slots=True)
class Interface(Def):
    type: InterfaceType


@define(eq=False, slots=True)
class Implementation(ASTNode):
    interface: InterfaceType
    implementing_type: SylvaType
    funcs: typing.List[Function]

    @classmethod
    def Def(cls, location, interface, implementing_type, funcs):
        impl = cls(
            location=location,
            interface=interface,
            implementing_type=implementing_type,
            funcs=funcs
        )
        interface.add_implementation(impl)
        implementing_type.add_implementation(impl)
        return impl

@define(eq=False, slots=True)
class EnumType(MetaSylvaLLVMType):
    values: typing.List[Expr] = field()
    implementations: typing.List = []

    # pylint: disable=unused-argument
    @values.validator
    def check_values(self, attribute, value):
        if len(value) <= 0:
            raise errors.EmptyEnum(self.location)

    @cache
    def get_llvm_type(self, module):
        return self.types[0].get_llvm_type(module)

    @cache
    def get_attribute(self, location, name):
        for val in self.values: # pylint: disable=not-an-iterable
            if val.name == name:
                return val

    @cached_property
    def names(self):
        return list(self.values.keys()) # pylint: disable=no-member

    @cached_property
    def types(self):
        return list(self.values.values()) # pylint: disable=no-member

    def check(self):
        super().check()

        first_type = self.types[0].type
        for value in self.types[1:]:
            if value.type != first_type:
                raise errors.MismatchedEnumMemberType(first_type, value)


@define(eq=False, slots=True)
class Variant(ParamTypeDef):
    pass


@define(eq=False, slots=True)
class CUnion(TypeDef):
    llvm_value: None | ir.Value = None


@define(eq=False, slots=True)
class GetElementPointerExpr(LLVMExpr):
    obj: TypeDef
    index: int
    name: str | None

    def emit_llvm_expr(self, module, builder):
        return builder.gep(
            self.obj, [self.index], inbounds=True, name=self.name
        )


class Builtins(enum.Enum):
    CVOID = IntegerType(location=Location.Generate(), bits=8, signed=True)
    BOOL = BooleanType(Location.Generate())
    C16 = ComplexType(location=Location.Generate(), bits=16)
    C32 = ComplexType(location=Location.Generate(), bits=32)
    C64 = ComplexType(location=Location.Generate(), bits=64)
    C128 = ComplexType(location=Location.Generate(), bits=128)
    CSTR = CStringType(Location.Generate())
    F16 = FloatType(location=Location.Generate(), bits=16)
    F32 = FloatType(location=Location.Generate(), bits=32)
    F64 = FloatType(location=Location.Generate(), bits=64)
    F128 = FloatType(location=Location.Generate(), bits=128)
    INT = IntegerType(
        location=Location.Generate(), bits=_SIZE_SIZE, signed=True
    )
    I8 = IntegerType(location=Location.Generate(), bits=8, signed=True)
    I16 = IntegerType(location=Location.Generate(), bits=16, signed=True)
    I32 = IntegerType(location=Location.Generate(), bits=32, signed=True)
    I64 = IntegerType(location=Location.Generate(), bits=64, signed=True)
    I128 = IntegerType(location=Location.Generate(), bits=128, signed=True)
    RUNE = RuneType(location=Location.Generate())
    STRING = StringType(location=Location.Generate())
    UINT = IntegerType(
        location=Location.Generate(), bits=_SIZE_SIZE, signed=False
    )
    U8 = IntegerType(location=Location.Generate(), bits=8, signed=False)
    U16 = IntegerType(location=Location.Generate(), bits=16, signed=False)
    U32 = IntegerType(location=Location.Generate(), bits=32, signed=False)
    U64 = IntegerType(location=Location.Generate(), bits=64, signed=False)
    U128 = IntegerType(
        location=Location.Generate(), bits=128, signed=False
    )
    ARRAY = ArrayType
    DYNARRAY = DynarrayType
    ENUM = EnumType
    VARIANT = VariantType
    STRUCT = StructType
    STR = StrType
    CARRAY = CArrayType
    CBITFIELD = CBitFieldType
    CBLOCKFUNCTION = CBlockFunctionType
    CFUNCTION = CFunctionType
    CPOINTER = CPointerType
    CSTRUCT = CStructType
    CUNION = CUnionType
