import platform
import tomllib

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from cdump import cdefs as CDefs
from cdump.parser import Parser

from sylva import errors
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
    STR,
    SylvaDef,
    SylvaField,
    SylvaType,
    SylvaValue,
    TypeDef,
    TypeModifier,
    get_int_type,
)
from sylva.const import ConstDef
from sylva.expr import LookupExpr
from sylva.location import Location
from sylva.mod import Mod


@dataclass(kw_only=True)
class CPackage:
    name: str
    os: str
    arch: str
    version: str
    header_files: list[Path] = field(default_factory=list)
    dynamic_libraries: list[Path] = field(default_factory=list)
    defs: dict[str, str] = field(default_factory=dict)
    typedefs: dict[str, str] = field(default_factory=dict)

    @classmethod
    def FromPath(cls, path: Path):
        os_name = platform.system().lower()
        arch = platform.machine().lower()
        with path.open('rb', encoding='utf-8') as fobj:
            d = tomllib.load(fobj)
            return {
                'name': d['package'],
                **d['package'][os_name][arch],
                **d['defs'][os_name][arch],
                **d['typedefs'][os_name][arch],
            }


class CModuleBuilder:

    def __init__(self, module: Mod, cdefs: list[CDefs.CDef]):
        self._module = module
        self._cdefs = cdefs

    @property
    def cdefs(self):
        return self._cdefs

    def _process_cdef(self, cdef):
        if isinstance(cdef, CDefs.Array):
            carray_type = (
                CPTR.build_type(
                    referenced_type=self._process_cdef(cdef.element_type)
                ) if cdef.element_count is None else CARRAY.build_type(
                    element_type=self._process_cdef(cdef.element_type),
                    element_count=cdef.element_count
                )
            )
            if cdef.name is None:
                return carray_type

            typedef = TypeDef(
                name=cdef.name.replace(' ', '_'), type=carray_type
            )

            self._module.add_def(typedef)

            return typedef
        if isinstance(cdef, CDefs.Enum):
            vals = []
            for name, value in cdef.values.items():
                # [NOTE] This should always end up some kind of integer
                type = self._process_cdef(cdef.type)
                val = ConstDef(
                    name=name,
                    type=type,
                    value=SylvaValue(type=type, value=value)
                )
                self.defs[val.name] = val
                vals.append(val)
            return vals
        if isinstance(cdef, CDefs.Function):
            cfn_def = SylvaDef(
                name=cdef.name,
                value=CFnValue(
                    type=CFN.build_type(
                        return_type=self._process_cdef(cdef.return_type),
                        parameters=[ # yapf: ignore
                            SylvaField(
                                name=name, type=self._process_cdef(type)
                            )
                            for name, type in cdef.parameters.items()
                        ],
                    ),
                    value=None
                ),
            )

            self._module.add_def(cfn_def)

            return cfn_def
        if isinstance(cdef, CDefs.FunctionPointer):
            return CFN.build_type(
                return_type=self._process_cdef(cdef.return_type),
                parameters=[ # yapf: ignore
                    SylvaField(
                        name=name, type=self._process_cdef(type)
                    )
                    for name, type in cdef.parameters.items()
                ],
            ),
        if isinstance(cdef, CDefs.Pointer):
            return CPTR.build_type(
                mod=TypeModifier.NoMod if cdef.is_const else TypeModifier.CMut,
                referenced_type=self._process_cdef(cdef.base_type)
            )
        if isinstance(cdef, CDefs.Reference):
            type = LookupExpr(
                name=cdef.target.replace(' ', '_'), type=SylvaType
            ).eval(self._module)
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
                return get_int_type(bits=cdef.size, signed=cdef.signed)

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
                            cstruct_type if cdef.name is not None and
                            name == cdef.name else self._process_cdef(type)
                        )
                    )
                )

            if not cdef.name:
                return cstruct_type

            type_def = TypeDef(
                name=cdef.name.replace(' ', '_'), type=cstruct_type
            )

            self._module.add_def(type_def)

            return type_def
        if isinstance(cdef, CDefs.Typedef):
            type_def = TypeDef(
                name=cdef.name,
                type=self._process_cdef(cdef.type),
            )

            self._module.add_def(type_def)

            return type_def
        if isinstance(cdef, CDefs.Union):
            cunion_type = CUNION.build_type()

            for name, type in cdef.fields.items():
                cunion_type.fields.append(
                    SylvaField(
                        name=name,
                        type=(
                            cunion_type if cdef.name is not None and
                            name == cdef.name else self._process_cdef(type)
                        )
                    )
                )

            if not cdef.name:
                return cunion_type

            type_def = TypeDef(name=cdef.name, type=cunion_type)

            self._module.add_def(type_def)

            return type_def
        if isinstance(cdef, CDefs.BlockFunctionPointer):
            return CBLOCKFN.build_type(
                return_type=self._process_cdef(cdef.return_type),
                parameters=[ # yapf: ignore
                    SylvaField(
                        name=name, type=self._process_cdef(type)
                    )
                    for name, type in cdef.parameters.items()
                ],
            ),
        raise Exception(f'Unknown C definition: {cdef} ({type(cdef)})')

    @classmethod
    def FromCPackage(
        cls,
        c_package: CPackage,
        preprocessor: Path,
        libclang: Optional[Path] = None
    ):
        module = Mod(name=c_package.name)

        for name, value in c_package.defs.items():
            module.add_def(
                ConstDef(
                    name=name,
                    value=SylvaValue(
                        type=STR.build_type(element_count=len(value)),
                        value=value
                    )
                )
            )

        for name, type_name in c_package.typedefs.items():
            type_def = LookupExpr(name=type_name).eval(module)
            if type_def is None:
                raise errors.UndefinedSymbolError(
                    Location.Generate(), name=type_name
                )

            if isinstance(type_def, TypeDef):
                module.add_def(TypeDef(name=name, type=type_def.type))
            else:
                raise Exception(f'Got non-typedef {type_def} for {type_name}')

        parser = Parser(preprocessor, libclang)

        return cls(
            module,
            [
                cdef for header_file in c_package.header_files
                for cdef in parser.parse(header_file)
            ]
        )

        builder = cls.FromLibcFiles(
            module, c_package.header_files, preprocessor, libclang
        )
        builder.build()
