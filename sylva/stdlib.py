from pathlib import Path

from antlr4 import FileStream


# [NOTE] We assume one module per file here, and that each file is named for
#        the module it contains.
_STDLIB_MODULE_NAMES = ['libc', 'sys']


class Stdlib:

    def __init__(self, streams):
        self.streams = streams

    @classmethod
    def FromPath(cls, path):
        stdlib_path = Path(path)
        if not stdlib_path.is_dir():
            raise ValueError(f'Expected {path} to be a stdlib folder')
        streams = []
        for module_name in _STDLIB_MODULE_NAMES:
            module_path = stdlib_path / f'{module_name}.sy'
            if not module_path.is_file():
                raise ValueError(
                    f'Expected {module_name} at {module_path} to be a file'
                )
            streams.append(FileStream(str(module_path)))
        return cls(streams)
