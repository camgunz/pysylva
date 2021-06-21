from . import ast


class CCodeGen:

    def __init__(self, program, output_folder):
        self.program = program
        self.output_folder = output_folder

    def compile_function(self, function):
        raise NotImplementedError()

    def compile_module(self, module):
        for obj in module.vars.values():
            if isinstance(obj, ast.Function):
                self.compile_function(obj)

    def compile(self):
        for module in self.program.modules.values():
            self.compile_module(module)
