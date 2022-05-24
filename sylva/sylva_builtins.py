from . import ast
from .location import Location


def get_module(program):
    module = ast.ModuleDef(program, '@builtin', [], [])

    ast.TypeDef(
        location=Location.Generate(),
        name='cvoid',
        type=ast.TypeSingletons.CVOID.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='bool',
        type=ast.TypeSingletons.BOOL.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='c16',
        type=ast.TypeSingletons.C16.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='c32',
        type=ast.TypeSingletons.C32.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='c64',
        type=ast.TypeSingletons.C64.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='c128',
        type=ast.TypeSingletons.C128.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='cstr',
        type=ast.TypeSingletons.CSTR.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='f16',
        type=ast.TypeSingletons.F16.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='f32',
        type=ast.TypeSingletons.F32.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='f64',
        type=ast.TypeSingletons.F64.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='f128',
        type=ast.TypeSingletons.F128.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='int',
        type=ast.TypeSingletons.INT.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='i8',
        type=ast.TypeSingletons.I8.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='i16',
        type=ast.TypeSingletons.I16.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='i32',
        type=ast.TypeSingletons.I32.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='i64',
        type=ast.TypeSingletons.I64.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='i128',
        type=ast.TypeSingletons.I128.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='rune',
        type=ast.TypeSingletons.RUNE.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='uint',
        type=ast.TypeSingletons.UINT.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='u8',
        type=ast.TypeSingletons.U8.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='u16',
        type=ast.TypeSingletons.U16.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='u32',
        type=ast.TypeSingletons.U32.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='u64',
        type=ast.TypeSingletons.U64.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='u128',
        type=ast.TypeSingletons.U128.value
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='string',
        type=ast.TypeSingletons.STRING.value
    ).define(module)
    # module.vars['array'] = ast.TypeSingletons.ARRAY.value
    # module.vars['enum'] = ast.TypeSingletons.ENUM.value
    # module.vars['variant'] = ast.TypeSingletons.VARIANT.value
    # module.vars['struct'] = ast.TypeSingletons.STRUCT.value
    # module.vars['str'] = ast.TypeSingletons.STR.value
    # module.vars['dynarray'] = ast.TypeSingletons.DYNARRAY.value
    # module.vars['carray'] = ast.TypeSingletons.CARRAY.value
    # module.vars['cbitfield'] = ast.TypeSingletons.CBITFIELD.value
    # module.vars['cblockfn'] = ast.TypeSingletons.CBLOCKFUNCTION.value
    # module.vars['cfn'] = ast.TypeSingletons.CFUNCTION.value
    # module.vars['cptr'] = ast.TypeSingletons.CPOINTER.value
    # module.vars['cstruct'] = ast.TypeSingletons.CSTRUCT.value
    # module.vars['cunion'] = ast.TypeSingletons.CUNION.value

    # OK so here we're gonna impl something for `str`, which is akin to impl
    # something for `array` or `struct`. This is a thing we can do internally
    # we wouldn't allow externally.
    string_iface = ast.InterfaceType(
        functions=[
            ast.Attribute(
                location=Location.Generate(),
                name='get_length',
                type=ast.FunctionType(
                    location=Location.Generate(),
                    monomorphizations=[
                        ast.MonoFunctionType(
                            Location.Generate(),
                            parameters=[],
                            return_type=ast.TypeSingletons.UINT.value,
                        )
                    ]
                )
            )
        ]
    )

    ast.InterfaceDef(name='String', type=string_iface).define(module)

    def build_str_string_impl(new_str_type):
        get_length = ast.FunctionDef(
            name='get_length',
            type=ast.FunctionType(
                location=Location.Generate(),
                monomorphizations=[
                    ast.MonoFunctionType(
                        location=Location.Generate(),
                        parameters=[
                            ast.Parameter(
                                location=Location.Generate(),
                                name='self',
                                type=ast.ReferencePointerType(
                                    referenced_type=new_str_type,
                                    is_exclusive=False,
                                )
                            )
                        ],
                        return_type=ast.TypeSingletons.UINT.value
                    )
                ]
            ),
            code=[
                ast.ReturnStmt(
                    expr=ast.AttributeLookupExpr(
                        location=Location.Generate(),
                        type=ast.TypeSingletons.UINT.value,
                        attribute='element_count',
                        expr=ast.AttributeLookupExpr(
                            location=Location.Generate(), name='self'
                        ),
                        reflection=True
                    )
                )
            ]
        )

        impl = ast.Implementation(
            location=Location.Generate(),
            interface=string_iface,
            implementing_type=new_str_type,
            funcs=[get_length]
        )

        string_iface.add_implementation(impl)
        new_str_type.add_implementation(impl)

    ast.TypeSingletons.STR.value.add_implementation_builder(
        build_str_string_impl
    )

    get_length = ast.FunctionDef(
        name='get_length',
        type=ast.FunctionType(
            location=Location.Generate(),
            monomorphizations=[
                ast.MonoFunctionType(
                    parameters=[
                        ast.Parameter(
                            location=Location.Generate(),
                            name='self',
                            type=ast.ReferencePointerType(
                                referenced_type=(
                                    ast.TypeSingletons.STRING.value
                                ),
                                is_exclusive=False,
                            )
                        )
                    ],
                    return_type=ast.TypeSingletons.UINT.value
                )
            ]
        ),
        code=[
            ast.ReturnStmt(
                expr=ast.AttributeLookupExpr(
                    location=Location.Generate(),
                    type=ast.TypeSingletons.UINT.value,
                    attribute='len',
                    expr=ast.LookupExpr( # yapf: disable
                        location=Location.Generate(),
                        name='self'
                    ),
                    reflection=False
                )
            )
        ]
    )

    string_impl = ast.Implementation(
        location=Location.Generate(),
        interface=string_iface,
        implementing_type=ast.TypeSingletons.STRING.value,
        funcs=[get_length]
    )

    string_iface.add_implementation(string_impl)
    ast.TypeSingletons.STRING.value.add_implementation(string_impl)

    return module
