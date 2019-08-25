from . import objects
from . import types


def add_to_program(program):
    _add_builtin_types(program)
    _add_libc_module(program)
    # _add_libc_functions(program)
    _add_builtin_modules(program)


def _add_builtin_types(program):
    module = program.get_builtin_module()
    module.define('bool', types.Boolean)
    module.define('rune', types.Rune)
    module.define('str', types.String)
    module.define('dec', types.Decimal)
    module.define('float', types.Float)
    module.define('integer', types.Integer)


def _add_libc_module(program):
    builtin_module = program.get_builtin_module()
    libc_module = program.get_module('libc')
    # So basically there has to be something that says, "this is a C function
    # call" and "this is a C function type".u So:
    # - Add the C types to `libc`
    libc_module.define('fputs', objects.Function(
        Location.Generate(),
        'fputs',
        [('message', builtin_module.lookup('str'))],
        []
    ))

def _add_builtin_modules(program):
    builtin_module = program.get_builtin_module()
    # Actually I think there will be a 'libc' module?
    sys_module = program.get_module('sys')
    sys_module.define('die', objects.Function(
        Location.Generate(),
        'die',
        [('message', builtin_module.lookup('str'))],
        []
    ))
    sys_module.define('exit', objects.Function(
        Location.Generate(),
        'exit',
        [('message', builtin_module.lookup('str')),
         ('code', builtin_module.lookup('int32'))],
        []
    ))
    sys_module.define('print', objects.Function(
        Location.Generate(),
        'print',
        [('message', builtin_module.lookup('str'))],
        []
    ))
    sys_module.define('echo', objects.Function(
        Location.Generate(),
        'echo',
        [('message', builtin_module.lookup('str'))],
        []
    ))
