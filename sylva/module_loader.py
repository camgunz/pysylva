from collections import defaultdict

from . import sylva

from .keyword_scanner import ExternScanner, ModuleScanner, ScannedItem
from .location import Location
from .module import Module


class ModuleLoader:

    @staticmethod
    def get_module_statements_from_locations(locations):
        module_statements = []
        for location in locations:
            ds_module_statements = ModuleScanner.scan(location)
            if not ds_module_statements:
                module_statements.append(ScannedItem(
                    location.copy(),
                    sylva.MAIN_MODULE_NAME
                ))
            else:
                first = ds_module_statements[0].location
                if not first.is_beginning:
                    ds_module_statements.insert(0, ScannedItem(
                        Location(first.location.data_source),
                        sylva.MAIN_MODULE_NAME
                    ))
                module_statements.extend(ds_module_statements)
        return module_statements

    @staticmethod
    def gather_dependencies_from_locations(locations):
        dependencies = set()
        for location in locations:
            extern_statements = ExternScanner.scan(location)
            extern_names = [es.name for es in extern_statements]
            dependencies.update(extern_names)
        return dependencies

    @staticmethod
    def load_from_locations(program, locations):
        names_to_locations = defaultdict(list)
        module_statements = (
            ModuleLoader.get_module_statements_from_locations(locations)
        )
        for module_statement in module_statements:
            location = module_statement.location
            data_source = location.make_data_source()
            subsequent_module_statements = [
                ms for ms in module_statements if ms.location > location
            ]
            if subsequent_module_statements:
                next_module_statement = subsequent_module_statements[0]
                next_location = next_module_statement.location
                data_source.set_end(next_location)
            location.data_source = data_source
            names_to_locations[module_statement.name].append(location)
        return [Module(
            program,
            name,
            locations,
            ModuleLoader.gather_dependencies_from_locations(locations)
        ) for name, locations in names_to_locations.items()]
