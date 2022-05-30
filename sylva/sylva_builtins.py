from . import ast, sylva
from .location import Location


def get_module(program):
    module = ast.Mod(
        name=sylva.BUILTIN_MODULE_NAME,
        program=program,
        streams=[],
        requirement_statements=[]
    )

    ast.TypeDef(
        location=Location.Generate(), name='c16', type=ast.TypeSingletons.C16
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='c32', type=ast.TypeSingletons.C32
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='c64', type=ast.TypeSingletons.C64
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='c128',
        type=ast.TypeSingletons.C128
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='f16', type=ast.TypeSingletons.F16
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='f32', type=ast.TypeSingletons.F32
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='f64', type=ast.TypeSingletons.F64
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='f128',
        type=ast.TypeSingletons.F128
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='i8', type=ast.TypeSingletons.I8
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='i16', type=ast.TypeSingletons.I16
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='i32', type=ast.TypeSingletons.I32
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='i64', type=ast.TypeSingletons.I64
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='i128',
        type=ast.TypeSingletons.I128
    ).define(module)
    ast.Alias(
        location=Location.Generate(), name='int', value=ast.TypeSingletons.INT
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='u8', type=ast.TypeSingletons.U8
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='u16', type=ast.TypeSingletons.U16
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='u32', type=ast.TypeSingletons.U32
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(), name='u64', type=ast.TypeSingletons.U64
    ).define(module)
    ast.Alias(
        location=Location.Generate(),
        name='uint',
        value=ast.TypeSingletons.UINT
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='u128',
        type=ast.TypeSingletons.U128
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='bool',
        type=ast.TypeSingletons.BOOL
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='rune',
        type=ast.TypeSingletons.RUNE
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='string',
        type=ast.TypeSingletons.STRING
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='cstr',
        type=ast.TypeSingletons.CSTR
    ).define(module)
    ast.TypeDef(
        location=Location.Generate(),
        name='cvoid',
        type=ast.TypeSingletons.CVOID
    ).define(module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='cptr',
    #     type=ast.TypeSingletons.CPTR
    # ).define(module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='carray',
    #     type=ast.TypeSingletons.CARRAY
    # ).define(module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='cunion',
    #     type=ast.TypeSingletons.CUNION
    # ).define(module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='array',
    #     type=ast.TypeSingletons.ARRAY
    # ).define(module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='dynarray',
    #     type=ast.TypeSingletons.DYNARRAY
    # ).define(module)
    # ast.TypeDef(
    #     location=Location.Generate(), name='str', type=ast.TypeSingletons.STR
    # ).define(module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='struct',
    #     type=ast.TypeSingletons.STRUCT
    # ).define(module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='variant',
    #     type=ast.TypeSingletons.VARIANT
    # ).define(module)
    ast.IfaceDef(
        location=Location.Generate(),
        name='Array',
        type=ast.IfaceSingletons.ARRAY.value
    ).define(module)
    ast.IfaceDef(
        location=Location.Generate(),
        name='String',
        type=ast.IfaceSingletons.STRING.value
    ).define(module)

    # module.vars['enum'] = ast.TypeSingletons.ENUM
    # module.vars['cbitfield'] = ast.TypeSingletons.CBITFIELD
    # module.vars['cblockfn'] = ast.TypeSingletons.CBLOCKFUNCTION
    # module.vars['cfn'] = ast.TypeSingletons.CFUNCTION
    # module.vars['cstruct'] = ast.TypeSingletons.CSTRUCT

    return module
