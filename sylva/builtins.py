from . import types


def add_to_program(program):
    _add_builtin_types(program)
    _add_builtin_modules(program)


def _add_builtin_types(program):
    module = program.get_builtin_module()
    module.define('bool', types.Boolean)
    module.define('rune', types.Rune)
    module.define('str', types.String)
    module.define('dec', types.Decimal)
    module.define('float', types.Float)
    module.define('integer', types.Integer)


def _add_builtin_modules(program):
    sys_module = program.get_module('sys')
