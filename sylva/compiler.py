import llvmlite.binding

from .target import Target

class Compiler:

    def __init__(self, target_triple=None):
        llvmlite.binding.initialize()
        llvmlite.binding.initialize_all_targets()
        llvmlite.binding.initialize_all_asmprinters()
        self.target = Target(target_triple)
