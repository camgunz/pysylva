from dataclasses import dataclass
from typing import TYPE_CHECKING

from cdump import cdefs as CDefs  # type: ignore

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
    F16,
    F32,
    F64,
    F128,
    SylvaDef,
    SylvaField,
    SylvaValue,
    TypeDef,
    TypeModifier,
    get_int_type,
)
from sylva.expr import LookupExpr
from sylva.mod import Mod
from sylva.package import CLibPackage
from sylva.parser import Parser as SylvaParser

if TYPE_CHECKING:
    from sylva.program import Program


@dataclass(kw_only=True, slots=True)
class CModuleLoader:
    program: 'Program'

    def _process_cdef(self, module: Mod, cdef: CDefs.CDef):
        if isinstance(cdef, CDefs.Array):
            carray_type = (
                CPTR.build_type(
                    referenced_type=self
                    ._process_cdef(module, cdef.element_type)
                ) if cdef.element_count is None else CARRAY.build_type(
                    element_type=self._process_cdef(module, cdef.element_type),
                    element_count=cdef.element_count
                )
            )
            if cdef.name is None:
                return carray_type

            typedef = TypeDef(
                name=cdef.name.replace(' ', '_'), type=carray_type
            )

            module.add_def(typedef)

            return typedef

        if isinstance(cdef, CDefs.Enum):
            vals = []
            for name, value in cdef.values.items():
                # [NOTE] This should always end up some kind of integer
                type = self._process_cdef(module, cdef.type)
                val = SylvaDef(
                    name=name, value=SylvaValue(type=type, value=value)
                )
                module.add_def(val)
                vals.append(val)
            return vals
        if isinstance(cdef, CDefs.Function):
            cfn_def = SylvaDef(
                name=cdef.name,
                value=CFnValue(
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
            )

            module.add_def(cfn_def)

            return cfn_def

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
            type = LookupExpr(name=cdef.target.replace(' ', '_')).eval(module)
            type.mod = (
                TypeModifier.NoMod if cdef.is_const else TypeModifier.CMut
            )
            return LookupExpr(name=cdef.target, type=type)

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

            raise ValueError(f'Unsupported builtin type {type(cdef)}')

        if isinstance(cdef, CDefs.Struct):
            cstruct_type = CSTRUCT.build_type()

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

            type_def = TypeDef(
                name=cdef.name.replace(' ', '_'), type=cstruct_type
            )

            module.add_def(type_def)

            return type_def

        if isinstance(cdef, CDefs.Typedef):
            type_def = TypeDef(
                name=cdef.name,
                type=self._process_cdef(module, cdef.type),
            )

            module.add_def(type_def)

            return type_def

        if isinstance(cdef, CDefs.Union):
            cunion_type = CUNION.build_type()

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

            type_def = TypeDef(name=cdef.name, type=cunion_type)

            module.add_def(type_def)

            return type_def

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

        raise Exception(f'Unknown C definition: {cdef} ({type(cdef)})')

    def load_package(self, package: CLibPackage):
        module = Mod(package=package, name=package.name)
        literal_expr_parser = SylvaParser(start='_literal_expr')
        type_expr_parser = SylvaParser(start='_type_expr')

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
