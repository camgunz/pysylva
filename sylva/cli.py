import argparse
import logging
import traceback

from pathlib import Path

import lark

from sylva import errors, debug, debugging
from sylva.program import Program
from sylva.stream import Stream


def print_bar(msg):
    """Prints a message in bar form."""
    caption = msg.join((' ', ' '))
    right_bar_count = 11
    total_width = 79
    bracket_count = 2
    left_bar_count = (
        total_width - bracket_count - right_bar_count - len(caption)
    )
    print()
    print('[%s]' % ('=' * (total_width - bracket_count)))
    print('[%s%s%s]' % ('=' * left_bar_count, caption, '=' * right_bar_count))
    print('[%s]' % ('=' * (total_width - bracket_count)))
    print()


def _load_program(file_paths, search_paths, target_triple=None):
    return Program([Stream.FromFile(str(p)) for p in file_paths], search_paths)


def parse(file_paths, search_paths, target_triple=None):
    """Parses files and prints output."""
    print_bar('Parsing')

    try:
        program = _load_program(file_paths, search_paths, target_triple)
        print(program.parse().pretty())
    except errors.SylvaError as error:
        debug('main', traceback.format_exc())
        print(error.pformat())


# pylint: disable=redefined-builtin
def compile(file_paths, output_folder, search_paths, target_triple=None):
    """Compiles files."""
    print_bar('Compiling')

    try:
        program = _load_program(file_paths, search_paths, target_triple)
        program_errors = program.compile(output_folder)
        for error in program_errors:
            print(error.pformat(), end='\n\n')
    except errors.SylvaError as error:
        debug('main', traceback.format_exc())
        print(error.pformat())


def run():
    """Main function."""
    if debugging('parser'):
        lark.logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(description='Sylva')
    parser.add_argument(
        '--only-parse', action='store_true', help='Only perform parsing'
    )
    parser.add_argument(
        '--search-paths', type=Path, nargs='+', help='Module search paths'
    )
    parser.add_argument('--target', type=str, help='Compilation target')
    parser.add_argument(
        '--output-folder', type=Path, required=True, help='Output folder'
    )
    parser.add_argument('files', type=Path, nargs='+', help='Files to compile')

    args = parser.parse_args()

    if args.only_parse:
        parse(args.files, args.search_paths, args.target)
    else:
        compile(args.files, args.output_folder, args.search_paths, args.target)


if __name__ == '__main__':
    run()
