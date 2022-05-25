import ctypes

import llvmlite.binding # type: ignore


_TARGET = None


class Target:

    def __init__(self, target_triple=None):
        llvmlite.binding.initialize()
        llvmlite.binding.initialize_all_targets()
        llvmlite.binding.initialize_all_asmprinters()
        if target_triple:
            self._target = llvmlite.binding.Target(target_triple)
        else:
            self._target = llvmlite.binding.Target.from_default_triple()
        self._machine = self._target.create_target_machine(codemodel='small')
        self._size_size = ctypes.sizeof(ctypes.c_size_t) * 8

    @property
    def machine(self):
        return self._machine

    @property
    def data(self):
        return self.machine.target_data

    @property
    def size_size(self):
        return self._size_size


def get_target():
    if _TARGET is None:
        raise NameError('Target undefined')
    return _TARGET


def make_target(target_triple=None):
    global _TARGET
    _TARGET = Target(target_triple=target_triple)
