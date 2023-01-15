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
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='c32', type=ast.TypeSingletons.C32
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='c64', type=ast.TypeSingletons.C64
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(),
        name='c128',
        type=ast.TypeSingletons.C128
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='f16', type=ast.TypeSingletons.F16
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='f32', type=ast.TypeSingletons.F32
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='f64', type=ast.TypeSingletons.F64
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(),
        name='f128',
        type=ast.TypeSingletons.F128
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='i8', type=ast.TypeSingletons.I8
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='i16', type=ast.TypeSingletons.I16
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='i32', type=ast.TypeSingletons.I32
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='i64', type=ast.TypeSingletons.I64
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(),
        name='i128',
        type=ast.TypeSingletons.I128
    ).emit(module=module)
    ast.Alias(
        location=Location.Generate(), name='int', value=ast.TypeSingletons.INT
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='u8', type=ast.TypeSingletons.U8
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='u16', type=ast.TypeSingletons.U16
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='u32', type=ast.TypeSingletons.U32
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(), name='u64', type=ast.TypeSingletons.U64
    ).emit(module=module)
    ast.Alias(
        location=Location.Generate(),
        name='uint',
        value=ast.TypeSingletons.UINT
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(),
        name='u128',
        type=ast.TypeSingletons.U128
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(),
        name='bool',
        type=ast.TypeSingletons.BOOL
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(),
        name='rune',
        type=ast.TypeSingletons.RUNE
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(),
        name='string',
        type=ast.TypeSingletons.STRING
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(),
        name='cstr',
        type=ast.TypeSingletons.CSTR
    ).emit(module=module)
    ast.TypeDef(
        location=Location.Generate(),
        name='cvoid',
        type=ast.TypeSingletons.CVOID
    ).emit(module=module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='cptr',
    #     type=ast.TypeSingletons.CPTR
    # ).emit(module=module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='carray',
    #     type=ast.TypeSingletons.CARRAY
    # ).emit(module=module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='cunion',
    #     type=ast.TypeSingletons.CUNION
    # ).emit(module=module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='array',
    #     type=ast.TypeSingletons.ARRAY
    # ).emit(module=module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='dynarray',
    #     type=ast.TypeSingletons.DYNARRAY
    # ).emit(module=module)
    # ast.TypeDef(
    #     location=Location.Generate(), name='str', type=ast.TypeSingletons.STR
    # ).emit(module=module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='struct',
    #     type=ast.TypeSingletons.STRUCT
    # ).emit(module=module)
    # ast.TypeDef(
    #     location=Location.Generate(),
    #     name='variant',
    #     type=ast.TypeSingletons.VARIANT
    # ).emit(module=module)
    ast.IfaceDef(
        location=Location.Generate(),
        name='Array',
        type=ast.IfaceSingletons.ARRAY.value
    ).emit(module=module)
    ast.IfaceDef(
        location=Location.Generate(),
        name='String',
        type=ast.IfaceSingletons.STRING.value
    ).emit(module=module)

    # module.vars['enum'] = ast.TypeSingletons.ENUM
    # module.vars['cbitfield'] = ast.TypeSingletons.CBITFIELD
    # module.vars['cblockfn'] = ast.TypeSingletons.CBLOCKFUNCTION
    # module.vars['cfn'] = ast.TypeSingletons.CFUNCTION
    # module.vars['cstruct'] = ast.TypeSingletons.CSTRUCT

    return module
