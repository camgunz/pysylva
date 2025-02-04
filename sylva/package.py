import platform

from dataclasses import field
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Any, Literal

from pydantic.dataclasses import dataclass
from semver import VersionInfo  # type: ignore

from sylva import errors
from sylva.stream import Stream
from sylva.utils import read_toml_file


class Arch(Enum):
    ANY = 'any'
    ARM = 'arm'
    ARMV9 = 'armv9'
    ARMV8 = 'armv8'
    ARMV7 = 'armv7'
    ARMV6 = 'armv6'
    ARMV5 = 'armv5'
    ARMV4 = 'armv4'
    ARM64 = 'arm64'
    ARMEB = 'armeb'
    AARCH64 = 'aarch64'
    AARCH64_BE = 'aarch64_be'
    AARCH64_32 = 'aarch64_32'
    ARC = 'arc'
    AVR = 'avr'
    BPFEL = 'bpfel'
    BPFEB = 'bpfeb'
    CSKY = 'csky'
    DXIL = 'dxil'
    HEXAGON = 'hexagon'
    LOONGARCH32 = 'loongarch32'
    LOONGARCH64 = 'loongarch64'
    M68K = 'm68k'
    MIPS = 'mips'
    MIPSEL = 'mipsel'
    MIPS64 = 'mips64'
    MIPS64EL = 'mips64el'
    MSP430 = 'msp430'
    PPC = 'ppc'
    PPCLE = 'ppcle'
    PPC64 = 'ppc64'
    PPC64LE = 'ppc64le'
    R600 = 'r600'
    AMDGCN = 'amdgcn'
    RISCV32 = 'riscv32'
    RISCV64 = 'riscv64'
    SPARC = 'sparc'
    SPARCV9 = 'sparcv9'
    SPARCEL = 'sparcel'
    SYSTEMZ = 'systemz'
    TCE = 'tce'
    TCELE = 'tcele'
    THUMB = 'thumb'
    THUMBEB = 'thumbeb'
    X86 = 'x86'
    X86_64 = 'x86_64'
    XCORE = 'xcore'
    XTENSA = 'xtensa'
    NVPTX = 'nvptx'
    NVPTX64 = 'nvptx64'
    LE32 = 'le32'
    LE64 = 'le64'
    AMDIL = 'amdil'
    AMDIL64 = 'amdil64'
    HSAIL = 'hsail'
    HSAIL64 = 'hsail64'
    SPIR = 'spir'
    SPIR64 = 'spir64'
    SPIRV32 = 'spirv32'
    SPIRV64 = 'spirv64'
    KALIMBA = 'kalimba'
    SHAVE = 'shave'
    LANAI = 'lanai'
    WASM32 = 'wasm32'
    WASM64 = 'wasm64'
    RENDERSCRIPT32 = 'renderscript32'
    RENDERSCRIPT64 = 'renderscript64'
    VE = 've '


class Vendor(Enum):
    ANY = 'any'
    AMD = 'amd'
    APPLE = 'apple'
    CSR = 'csr'
    FREESCALE = 'freescale'
    IBM = 'ibm'
    IMAGINATION_TECHNOLOGIES = 'imagination_technologies'
    MESA = 'mesa'
    MIPS_TECHNOLOGIES = 'mips_technologies'
    MYRIAD = 'myriad'
    NVIDIA = 'nvidia'
    OPEN_EMBEDDED = 'open_embedded'
    PC = 'pc'
    SCEI = 'scei'
    SUSE = 'suse'


class OS(Enum):
    ANY = 'any'
    AIX = 'aix'
    AMDHSA = 'amdhsa'
    AMDPAL = 'amdpal'
    ANANAS = 'ananas'
    CUDA = 'cuda'
    CLOUDABI = 'cloudabi'
    CONTIKI = 'contiki'
    DARWIN = 'darwin'
    DRAGONFLY = 'dragonfly'
    DRIVERKIT = 'driverkit'
    ELFIAMCU = 'elfiamcu'
    EMSCRIPTEN = 'emscripten'
    FREEBSD = 'freebsd'
    FUCHSIA = 'fuchsia'
    HAIKU = 'haiku'
    HERMITCORE = 'hermitcore'
    HURD = 'hurd'
    IOS = 'ios'
    KFREEBSD = 'kfreebsd'
    LINUX = 'linux'
    LITEOS = 'liteos '
    LV2 = 'lv2'
    MACOSX = 'macosx'
    MESA3D = 'mesa3d'
    MINIX = 'minix'
    NVCL = 'nvcl'
    NACL = 'nacl'
    NETBSD = 'netbsd'
    OPENBSD = 'openbsd'
    PS4 = 'ps4'
    PS5 = 'ps5'
    RTEMS = 'rtems'
    SHADERMODEL = 'shadermodel'
    SOLARIS = 'solaris'
    TVOS = 'tvos'
    WASI = 'wasi'
    WATCHOS = 'watchos'
    WIN32 = 'win32'
    ZOS = 'zos'


class Environment(Enum):
    ANY = 'any'
    AMPLIFICATION = 'amplification'
    ANDROID = 'android'
    ANYHIT = 'anyhit'
    CODE16 = 'code16'
    CALLABLE = 'callable'
    CLOSESTHIT = 'closesthit'
    COMPUTE = 'compute'
    CORECLR = 'coreclr'
    CYGNUS = 'cygnus'
    DOMAIN = 'domain'
    EABI = 'eabi'
    EABIHF = 'eabihf'
    GNU = 'gnu'
    GNUABI64 = 'gnuabi64'
    GNUABIN32 = 'gnuabin32'
    GNUEABI = 'gnueabi'
    GNUEABIHF = 'gnueabihf'
    GNUF32 = 'gnuf32'
    GNUF64 = 'gnuf64'
    GNUILP32 = 'gnuilp32'
    GNUSF = 'gnusf'
    GNUX32 = 'gnux32'
    GEOMETRY = 'geometry'
    HULL = 'hull'
    INTERSECTION = 'intersection'
    ITANIUM = 'itanium'
    LIBRARY = 'library'
    MSVC = 'msvc'
    MACABI = 'macabi'
    MESH = 'mesh'
    MISS = 'miss'
    MUSL = 'musl'
    MUSLEABI = 'musleabi'
    MUSLEABIHF = 'musleabihf'
    MUSLX32 = 'muslx32'
    OPENHOS = 'openhos'
    PIXEL = 'pixel'
    RAYGENERATION = 'raygeneration'
    SIMULATOR = 'simulator'
    VERTEX = 'vertex'


class ObjectFormat(Enum):
    ANY = 'any'
    COFF = 'coff'
    DXCONTAINER = 'dxcontainer'
    ELF = 'elf'
    GOFF = 'goff'
    MACHO = 'macho'
    SPIRV = 'spirv'
    WASM = 'wasm'
    XCOFF = 'xcoff'


@dataclass(kw_only=True, frozen=True)
class Target:
    arch: Arch = Arch.ANY
    vendor: Vendor = Vendor.ANY
    os: OS = OS.ANY
    environment: Environment = Environment.ANY
    object_format: ObjectFormat = ObjectFormat.ANY
    header_files: list[Path] = field(default_factory=list, repr=False)
    dynamic_libraries: list[Path] = field(default_factory=list)
    static_libraries: list[Path] = field(default_factory=list)
    defs: dict[str, str] = field(default_factory=dict)
    macro_defs: dict[str, str] = field(default_factory=dict)
    type_defs: dict[str, str] = field(default_factory=dict)


@dataclass(kw_only=True, frozen=True)
class Dependency:
    name: str
    location: str
    min_version: str | None = None
    max_version: str | None = None


@dataclass(kw_only=True, frozen=True)
class BasePackage:
    path: Path
    name: str
    version: str

    @cached_property
    def semver(self):
        return VersionInfo.parse(self.version)

    def get_streams(self):
        raise NotImplementedError()


@dataclass(kw_only=True, frozen=True)
class SylvaPackage(BasePackage):
    type: Literal['bin', 'lib']
    source_files: list[Path] = field(default_factory=list, repr=False)
    dependencies: list[Dependency] = field(default_factory=list)

    @classmethod
    def FromPath(cls, path: Path):
        kwargs: dict[str, Any] = {
            'path': path.parent.absolute(),
            **read_toml_file(path),
        }

        return cls(**kwargs)

    def __post_init__(self):
        if self.type not in ['bin', 'lib']:
            raise ValueError('"type" must be either "bin" or "lib"')

    def get_streams(self):
        return [
            Stream.FromPath(sf if sf.is_absolute() else self.path / sf)
            for sf in map(Path, self.source_files)
        ]


@dataclass(kw_only=True, frozen=True)
class CLibPackage(BasePackage):
    type: Literal['clib']
    targets: list[Target] = field(default_factory=list)

    def __post_init__(self):
        if self.type != 'clib':
            raise ValueError('"type" must be "clib"')

    @cached_property
    def target(self):
        arch = platform.machine().lower()
        os = platform.system().lower()

        usable_targets = [
            t for t in self.targets
            if t.arch.value == arch and t.os.value == os
        ]

        if not usable_targets:
            raise errors.NoUsableCLibTargets(self.name, arch, os)

        return usable_targets[0]

    @cached_property
    def header_files(self):
        paths = [Path(hf) for hf in self.target.header_files]
        return [p if p.is_absolute() else self.path / p for p in paths]

    @cached_property
    def dynamic_libraries(self):
        paths = [Path(dl) for dl in self.target.dynamic_libraries]
        return [p if p.is_absolute() else self.path / p for p in paths]

    @cached_property
    def static_libraries(self):
        paths = [Path(sl) for sl in self.target.static_libraries]
        return [p if p.is_absolute() else self.path / p for p in paths]

    @property
    def defs(self):
        return self.target.defs

    @property
    def macro_defs(self):
        return self.target.macro_defs

    @property
    def type_defs(self):
        return self.target.type_defs

    def get_streams(self):
        return [Stream.FromPath(hf) for hf in self.header_files]


def get_package_from_path(package_file: Path) -> BasePackage:
    package_def = read_toml_file(package_file)
    kwargs = {'path': package_file.parent.absolute(), **package_def}
    P = SylvaPackage if package_def['type'] in ['bin', 'lib'] else CLibPackage
    return P(**kwargs)
