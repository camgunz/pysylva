import llvmlite.binding

from llvmlite import ir

from . import debug, types


class Compiler:

    def __init__(self, target_triple=None):
        llvmlite.binding.initialize()
        llvmlite.binding.initialize_all_targets()
        llvmlite.binding.initialize_all_asmprinters()
        if target_triple:
            target = llvmlite.binding.Target(target_triple)
        else:
            target = llvmlite.binding.Target.from_default_triple()
        self.target_machine = target.create_target_machine(codemodel='small')
        self._current_module = None

    def compile_const(self, const):
        raise NotImplementedError()

    def compile_enum(self, enum):
        raise NotImplementedError()

    def compile_function_type(self, function_type):
        raise NotImplementedError()

    def compile_c_function_type(self, c_function_type):
        raise NotImplementedError()

    def compile_c_block_function_type(self, c_block_function_type):
        raise NotImplementedError()

    def compile_function(self, function):
        raise NotImplementedError()

    def compile_interface(self, interface):
        raise NotImplementedError()

    def compile_implementation(self, implementation):
        raise NotImplementedError()

    def compile_range(self, range):
        raise NotImplementedError()

    def compile_struct(self, struct):
        raise NotImplementedError()

    def compile_c_struct(self, c_struct):
        raise NotImplementedError()

    def compile_c_union(self, c_union):
        raise NotImplementedError()

    def get_identified_type(self, name):
        return self._current_module.context.get_identified_type(name)

    def compile_module(self, module):
        # llvm_module = ir.Module(name=module.name, context=ir.Context())
        llvm_module = ir.Module(name=module.name)
        self._current_module = llvm_module
        for name, obj in module.vars.items():
            if isinstance(obj, types.CFunction):
                debug('compile', f'Adding cfunction {name}')
                ir.Function(llvm_module, obj.get_llvm_type(self), name)
            elif isinstance(obj, types.CStruct):
                debug('compile', f'Adding cstruct {name}')
                ir.GlobalVariable(
                    llvm_module, obj.get_llvm_type(self, name), name
                )
            elif isinstance(obj, types.CUnion):
                debug('compile', f'Adding cunion {name}')
                ir.GlobalVariable(llvm_module, obj.get_llvm_type(self), name)
            elif isinstance(obj, types.Function):
                debug('compile', f'Adding function {name}')
                func = ir.Function(llvm_module, obj.get_llvm_type(self), name)
                # [TODO] Handle code block
            elif isinstance(obj, types.Struct):
                debug('compile', f'Adding struct {name}')
                ir.GlobalVariable(llvm_module, obj.get_llvm_type(self), name)
            # elif isinstance(obj, types.CFunctionType):
            #     self.compile_c_function_type(obj)
            # elif isinstance(obj, types.CBlockFunctionType):
            #     self.compile_c_block_function_type(obj)
            # elif isinstance(obj, types.Enum):
            #     self.compile_enum(obj)
            # elif isinstance(obj, types.FunctionType):
            #     self.compile_function_type(obj)
            # elif isinstance(obj, types.Interface):
            #     self.compile_interface(obj)
            # elif isinstance(obj, types.Range):
            #     self.compile_range(obj)

        self._current_module = None
        llvm_ir = str(llvm_module)
        print(llvm_ir)
        llvm_mod = llvmlite.binding.parse_assembly(llvm_ir)
        llvm_mod.verify()
        return self.target_machine.emit_object(llvm_mod)
