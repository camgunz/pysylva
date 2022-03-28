import llvmlite.binding

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

    @staticmethod
    def compile_ir_to_module(ir):
        mod = llvmlite.binding.parse_assembly(ir)
        mod.verify()
        return mod

    def compile_ir_to_object_code(self, ir):
        return self.target_machine.emit_object(self.compile_ir_to_module(ir))

    def compile_ir_to_file(self, ir, file_path):
        with open(file_path, 'wb') as fobj:
            fobj.write(self.compile_ir_to_object_code(ir))
