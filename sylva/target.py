import llvmlite.binding

class TargetTypeInfo:

    __slots__ = ('size', 'alignment')

    def __init__(self, size, alignment):
        self.size = size
        self.alignment = alignment

# pylint: disable=too-many-instance-attributes
class Target:

    def __init__(self, triple=None):
        triple = triple or llvmlite.binding.get_default_triple()
        self._target = llvmlite.binding.Target.from_triple(triple)
        self._target_machine = self._target.create_target_machine()
        int8_type = llvmlite.ir.IntType(8)
        int16_type = llvmlite.ir.IntType(16)
        int32_type = llvmlite.ir.IntType(32)
        int64_type = llvmlite.ir.IntType(64)
        int128_type = llvmlite.ir.IntType(128)
        int256_type = llvmlite.ir.IntType(256)
        f32_type = llvmlite.ir.FloatType()
        f64_type = llvmlite.ir.DoubleType()
        int8_pointer_type = llvmlite.ir.PointerType(int8_type)

        self.int8_type_info = TargetTypeInfo(
            int8_type.get_abi_size(self.data),
            int8_type.get_abi_alignment(self.data)
        )
        self.int16_type_info = TargetTypeInfo(
            int16_type.get_abi_size(self.data),
            int16_type.get_abi_alignment(self.data)
        )
        self.int32_type_info = TargetTypeInfo(
            int32_type.get_abi_size(self.data),
            int32_type.get_abi_alignment(self.data)
        )
        self.int64_type_info = TargetTypeInfo(
            int64_type.get_abi_size(self.data),
            int64_type.get_abi_alignment(self.data)
        )
        self.int128_type_info = TargetTypeInfo(
            int128_type.get_abi_size(self.data),
            int128_type.get_abi_alignment(self.data)
        )
        self.int256_type_info = TargetTypeInfo(
            int256_type.get_abi_size(self.data),
            int256_type.get_abi_alignment(self.data)
        )
        self.f32_type_info = TargetTypeInfo(
            f32_type.get_abi_size(self.data),
            f32_type.get_abi_alignment(self.data)
        )
        self.f64_type_info = TargetTypeInfo(
            f64_type.get_abi_size(self.data),
            f64_type.get_abi_alignment(self.data)
        )
        self.int8_pointer_type_info = TargetTypeInfo(
            int8_pointer_type.get_abi_size(self.data),
            int8_pointer_type.get_abi_alignment(self.data)
        )

        self.boolean_type_info = self.int8_pointer_type_info
        self.rune_type_info = self.int32_type_info
        self.string_type_info = self.int8_pointer_type_info

    @property
    def machine(self):
        return self._target_machine

    @property
    def data(self):
        return self.machine.target_data
