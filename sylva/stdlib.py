from pathlib import Path

from .data_source import DataSource


# [NOTE} We assume one module per file here, and that each file is named for
#        the module it contains.
_STDLIB_MODULE_NAMES = ['sys']


class Stdlib:

    def __init__(self, data_sources):
        self.data_sources = data_sources

    @classmethod
    def FromPath(cls, path):
        stdlib_path = Path(path)
        if not stdlib_path.is_dir():
            raise ValueError(f'Expected {path} to be a stdlib folder')
        data_sources = []
        for module_name in _STDLIB_MODULE_NAMES:
            module_path = stdlib_path / f'{module_name}.sy'
            if not module_path.is_file():
                raise ValueError(
                    f'Expected file for {module_name} at {module_path}'
                )
            data_sources.append(DataSource.FromPath(module_path))
        return cls(data_sources)
