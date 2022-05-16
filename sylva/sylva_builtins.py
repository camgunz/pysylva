from . import ast
from .location import Location
from .module import Module


def get_module(program):
    module = Module(program, '@builtin', [], [])

    module.vars['cvoid'] = ast.Builtins.CVOID.value
    module.vars['bool'] = ast.Builtins.BOOL.value
    module.vars['c16'] = ast.Builtins.C16.value
    module.vars['c32'] = ast.Builtins.C32.value
    module.vars['c64'] = ast.Builtins.C64.value
    module.vars['c128'] = ast.Builtins.C128.value
    module.vars['cstr'] = ast.Builtins.CSTR.value
    module.vars['f16'] = ast.Builtins.F16.value
    module.vars['f32'] = ast.Builtins.F32.value
    module.vars['f64'] = ast.Builtins.F64.value
    module.vars['f128'] = ast.Builtins.F128.value
    module.vars['int'] = ast.Builtins.INT.value
    module.vars['i8'] = ast.Builtins.I8.value
    module.vars['i16'] = ast.Builtins.I16.value
    module.vars['i32'] = ast.Builtins.I32.value
    module.vars['i64'] = ast.Builtins.I64.value
    module.vars['i128'] = ast.Builtins.I128.value
    module.vars['rune'] = ast.Builtins.RUNE.value
    module.vars['string'] = ast.Builtins.STRING.value
    module.vars['uint'] = ast.Builtins.UINT.value
    module.vars['u8'] = ast.Builtins.U8.value
    module.vars['u16'] = ast.Builtins.U16.value
    module.vars['u32'] = ast.Builtins.U32.value
    module.vars['u64'] = ast.Builtins.U64.value
    module.vars['u128'] = ast.Builtins.U128.value
    module.vars['array'] = ast.Builtins.ARRAY.value
    module.vars['dynarray'] = ast.Builtins.DYNARRAY.value
    module.vars['enum'] = ast.Builtins.ENUM.value
    module.vars['variant'] = ast.Builtins.VARIANT.value
    module.vars['struct'] = ast.Builtins.STRUCT.value
    module.vars['str'] = ast.Builtins.STR.value
    module.vars['carray'] = ast.Builtins.CARRAY.value
    module.vars['cbitfield'] = ast.Builtins.CBITFIELD.value
    module.vars['cblockfn'] = ast.Builtins.CBLOCKFUNCTION.value
    module.vars['cfn'] = ast.Builtins.CFUNCTION.value
    module.vars['cptr'] = ast.Builtins.CPOINTER.value
    module.vars['cstruct'] = ast.Builtins.CSTRUCT.value
    module.vars['cunion'] = ast.Builtins.CUNION.value

    # OK so here we're gonna impl something for `str`, which is akin to impl
    # something for `array` or `struct`. This is a thing we can do internally
    # we wouldn't allow externally.
    String = ast.InterfaceType(
        functions=[
            ast.Attribute(
                location=Location.Generate(),
                name='get_length',
                type=ast.FunctionType.Def(
                    location=Location.Generate(),
                    parameters=[],
                    return_type=ast.IntegerType.Platform(signed=False),
                )
            )
        ]
    )

    module.vars['String'] = String

    ast.Implementation.Def(
        location=Location.Generate(),
        interface=String,
        implementing_type=ast.Builtins.STR.value,
        funcs=[
            ast.Function(
                type=ast.FunctionType.Def(
                    location=Location.Generate(),
                    parameters=[
                        ast.Parameter(
                            location=Location.Generate(),
                            name='self',
                            type=ast.ReferencePointerType(
                                referenced_type=ast.Builtins.STR.value,
                                is_exclusive=False,
                            )
                        )
                    ],
                    return_type=ast.Builtins.UINT.value
                ),
                code=[
                    ast.Return(
                        expr=ast.AttributeLookupExpr(
                            location=Location.Generate(),
                            type=ast.Builtins.UINT.value,
                            attribute='element_count',
                            expr=ast.LookupExpr(
                                location=Location.Generate(), name='self'
                            ),
                            reflection=True
                        )
                    )
                ]
            )
        ]
    )

    ast.Implementation.Def(
        location=Location.Generate(),
        interface=String,
        implementing_type=ast.Builtins.STRING.value,
        funcs=[
            ast.Function(
                type=ast.FunctionType.Def(
                    location=Location.Generate(),
                    parameters=[
                        ast.Parameter(
                            location=Location.Generate(),
                            name='self',
                            type=ast.ReferencePointerType(
                                referenced_type=ast.Builtins.STR.value,
                                is_exclusive=False,
                            )
                        )
                    ],
                    return_type=ast.Builtins.UINT.value
                ),
                code=[
                    ast.Return(
                        expr=ast.AttributeLookupExpr(
                            location=Location.Generate(),
                            type=ast.Builtins.UINT.value,
                            attribute='len',
                            expr=ast.LookupExpr(
                                location=Location.Generate(), name='self'
                            ),
                            reflection=False
                        )
                    )
                ]
            )
        ]
    )

    return module
