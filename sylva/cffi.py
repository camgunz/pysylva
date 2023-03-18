from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Tuple, Union

from cdump import cdefs as CDefs  # type: ignore

from sylva import errors
from sylva.ast_builder import ASTBuilder
from sylva.builtins import (
    BOOL,
    C16,
    C32,
    C64,
    C128,
    CARRAY,
    CBLOCKFN,
    CFN,
    CFnValue,
    CPTR,
    CSTRUCT,
    CUNION,
    CVOID,
    CVOIDEX,
    ENUM,
    F16,
    F32,
    F64,
    F128,
    IntValue,
    SylvaDef,
    SylvaField,
    SylvaType,
    SylvaValue,
    TYPE,
    TypeDef,
    TypeModifier,
    get_int_type,
)
from sylva.expr import LookupExpr
from sylva.mod import Mod
from sylva.package import CLibPackage
from sylva.parser import Parser

if TYPE_CHECKING:
    from sylva.program import Program


@dataclass(kw_only=True, slots=True)
class CModuleLoader:
    program: 'Program'

    @staticmethod
    def add_def(
        module: Mod,
        name: str,
        value: Union[SylvaType, SylvaValue],
        use_existing: Optional[bool] = False
    ) -> Tuple[Union[SylvaType, SylvaValue], bool]:
        name = name.replace(' ', '_')

        if existing := module.lookup(name):
            if not isinstance(value, Mod) and use_existing:
                return (existing, False)  # type: ignore

            if isinstance(value, SylvaType) and value != existing:
                raise errors.IncompatibleTypeDefRedefinition(
                    name, type, existing
                )

            if (isinstance(value, SylvaValue) and
                    isinstance(existing, SylvaValue) and
                    value.type != existing.type):
                raise errors.IncompatibleTypeDefRedefinition(
                    name, type, existing
                )

            if isinstance(value, Mod):
                raise TypeError(
                    'We only expect either a SylvaDef or TypeDef here'
                )
            else:
                return (value, False)

        new_def: Union[SylvaDef, TypeDef] = (
            TypeDef(name=name, type=value) if isinstance(value, SylvaType) else
            SylvaDef(name=name, value=value)
        )

        module.add_def(new_def)

        return (value, True)

    def _process_cdef(self, module: Mod, cdef: CDefs.CDef):
        if isinstance(cdef, CDefs.Array):
            carray_type = (
                CPTR.build_type(
                    referenced_type=self
                    ._process_cdef(module, cdef.element_type)
                ) if cdef.element_count is None else CARRAY.build_type(
                    element_type=self._process_cdef(module, cdef.element_type),
                    element_count=IntValue(
                        type=get_int_type(bits=None, signed=False),
                        value=cdef.element_count
                    )
                )
            )
            if cdef.name is None:
                return carray_type

            return self.add_def(module, cdef.name, carray_type)[0]

        if isinstance(cdef, CDefs.Enum):
            enum_type = ENUM.build_type(
                values={ # yapf: ignore
                    name: SylvaValue(
                        # [NOTE] This should always be some kind of integer
                        type=self._process_cdef(module, cdef.type),
                        value=value,
                    )
                    for name, value in cdef.values.items()
                }
            )

            if not cdef.name:
                return enum_type

            return self.add_def(
                module, cdef.name, enum_type, use_existing=True
            )[0]

        if isinstance(cdef, CDefs.Function):
            return self.add_def(
                module,
                cdef.name,
                CFnValue(
                    type=CFN.build_type(
                        return_type=self._process_cdef(module, cdef.return_type),
                        parameters=[ # yapf: ignore
                            SylvaField(
                                name=name, type=self._process_cdef(module, type)
                            )
                            for name, type in cdef.parameters.items()
                        ],
                    ),
                    value=None
                ),
                use_existing=True
            )[0]

        if isinstance(cdef, CDefs.FunctionPointer):
            return CFN.build_type(
                return_type=self._process_cdef(module, cdef.return_type),
                parameters=[ # yapf: ignore
                    SylvaField(
                        name=name, type=self._process_cdef(module, type)
                    )
                    for name, type in cdef.parameters.items()
                ],
            ),

        if isinstance(cdef, CDefs.Pointer):
            return CPTR.build_type(
                mod=TypeModifier.NoMod if cdef.is_const else TypeModifier.CMut,
                referenced_type=self._process_cdef(module, cdef.base_type)
            )

        if isinstance(cdef, CDefs.Reference):
            mod = TypeModifier.NoMod if cdef.is_const else TypeModifier.CMut
            value = LookupExpr(
                name=cdef.target.replace(' ', '_'), type=TYPE
            ).eval(module)

            if not isinstance(value, SylvaType):
                raise Exception('We only expect a SylvaType here')

            value.mod = mod
            return value

        if isinstance(cdef, CDefs.ScalarType):
            if isinstance(cdef, CDefs.Void):
                return CVOID if cdef.is_const else CVOIDEX

            if isinstance(cdef, CDefs.Bool):
                return BOOL

            if isinstance(cdef, CDefs.Integer):
                return get_int_type(bits=cdef.size * 8, signed=cdef.is_signed)

            if isinstance(cdef, CDefs.FloatingPoint):
                if cdef.size == 2:
                    return F16
                if cdef.size == 4:
                    return F32
                if cdef.size == 8:
                    return F64
                if cdef.size == 16:
                    return F128

            if isinstance(cdef, CDefs.Complex):
                if cdef.size == 2:
                    return C16
                if cdef.size == 4:
                    return C32
                if cdef.size == 8:
                    return C64
                if cdef.size == 16:
                    return C128

            raise ValueError(f'Unsupported builtin type {cdef}')

        if isinstance(cdef, CDefs.Struct):
            cstruct_type = CSTRUCT.build_type()

            if cdef.name:
                cstruct_type_def, added = self.add_def(
                    module, cdef.name, cstruct_type, use_existing=True
                )

                if not added:
                    return cstruct_type_def

            for name, type in cdef.fields.items():
                if name == 'packed':
                    continue

                cstruct_type.fields.append(
                    SylvaField(
                        name=name,
                        type=(
                            cstruct_type
                            if cdef.name is not None and name == cdef.name else
                            self._process_cdef(module, type)
                        )
                    )
                )

            if not cdef.name:
                return cstruct_type

            return cstruct_type_def

        if isinstance(cdef, CDefs.Typedef):
            type = self._process_cdef(module, cdef.type)
            if isinstance(type, TypeDef):
                return type

            return self.add_def(module, cdef.name, type)[0]

        if isinstance(cdef, CDefs.Union):
            cunion_type = CUNION.build_type()

            if cdef.name:
                cunion_type_def, added = self.add_def(
                    module, cdef.name, cunion_type, use_existing=True
                )

                if not added:
                    return cunion_type_def

            for name, type in cdef.fields.items():
                cunion_type.fields.append(
                    SylvaField(
                        name=name,
                        type=(
                            cunion_type
                            if cdef.name is not None and name == cdef.name else
                            self._process_cdef(module, type)
                        )
                    )
                )

            if not cdef.name:
                return cunion_type

            return cunion_type_def

        if isinstance(cdef, CDefs.BlockFunctionPointer):
            return CBLOCKFN.build_type(
                return_type=self._process_cdef(module, cdef.return_type),
                parameters=[ # yapf: ignore
                    SylvaField(
                        name=name, type=self._process_cdef(module, type)
                    )
                    for name, type in cdef.parameters.items()
                ],
            )

        raise Exception(f'Unknown C definition: {cdef}')

    def load_package(self, package: CLibPackage):
        module = Mod(package=package, name=package.name, type=Mod.Type.C)
        literal_expr_parser = Parser(start='_literal_expr')
        type_expr_parser = Parser(start='_type_expr')

        for name, literal_expr_text in package.defs.items():
            tree = ASTBuilder(
                program=self.program, module=module
            ).transform(literal_expr_parser.parse(literal_expr_text))
            expr = tree.children[0]
            value = expr.eval(module)
            module.add_def(
                SylvaDef(
                    name=name, value=SylvaValue(type=expr.type, value=value)
                )
            )

        for name, type_expr_text in package.type_defs.items():
            tree = ASTBuilder(
                program=self.program, module=module
            ).transform(type_expr_parser.parse(type_expr_text))
            type = tree.children[0]

            module.add_def(TypeDef(name=name, type=type))

        for header_file in package.header_files:
            for cdef in self.program.c_parser.parse(header_file):
                self._process_cdef(module, cdef)

        return {module.name: module}
