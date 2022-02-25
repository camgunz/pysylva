import itertools

from collections import defaultdict

from . import sylva

from .keyword_scanner import RequirementScanner, ModuleScanner, ScannedItem
from .location import Location
from .module import Module


class ModuleLoader:

    @staticmethod
    def get_module_statements_from_data_sources(data_sources):
        module_statements = []
        for data_source in data_sources:
            ds_module_statements = ModuleScanner.scan(data_source)
            if not ds_module_statements:
                module_statements.append(ScannedItem(
                    Location(data_source),
                    sylva.MAIN_MODULE_NAME
                ))
            else:
                first = ds_module_statements[0].location
                if not first.is_top:
                    ds_module_statements.insert(0, ScannedItem(
                        Location(first.location.data_source),
                        sylva.MAIN_MODULE_NAME
                    ))
                module_statements.extend(ds_module_statements)
        return module_statements

    @staticmethod
    def gather_requirements_from_data_sources(data_sources):
        dep_lists = [RequirementScanner.scan(ds) for ds in data_sources]
        seen = set()
        return [
            dep for dep in itertools.chain(*dep_lists)
            if not dep.name in seen
            and not seen.add(dep.name)
        ]

    @staticmethod
    def load_from_data_sources(program, input_data_sources):
        names_to_data_sources = defaultdict(list)
        module_statements = (
            ModuleLoader.get_module_statements_from_data_sources(
                input_data_sources
            )
        )
        for module_statement in module_statements:
            location = module_statement.location
            data_source = location.data_source.copy()
            data_source.set_begin(location)
            subsequent_module_statements = [
                ms for ms in module_statements if ms.location > location
            ]
            if subsequent_module_statements:
                next_module_statement = sorted(subsequent_module_statements)[0]
                next_location = next_module_statement.location
                data_source.set_end(next_location)
            names_to_data_sources[module_statement.name].append(data_source)
        return [Module(
            program,
            name,
            data_sources,
            ModuleLoader.gather_requirements_from_data_sources(data_sources)
        ) for name, data_sources in names_to_data_sources.items()]
