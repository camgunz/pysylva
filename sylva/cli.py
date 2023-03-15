import argparse
import logging
import traceback

from pathlib import Path

import lark

from sylva import errors, debug, debugging
from sylva.package import get_package_from_path
from sylva.program import Program


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


def parse(package_folder, deps_folder, stdlib, cpp, libclang):
    """Parses files and prints output."""
    print_bar('Parsing')

    try:
        program = Program(
            package=get_package_from_path(package_folder / 'package.toml'),
            deps_folder=deps_folder,
            stdlib=stdlib,
            c_preprocessor=cpp,
            libclang=libclang
        )
        print(program.parse().pretty() and '')
    except errors.SylvaError as error:
        debug('main', traceback.format_exc())
        print(error.pformat())


def compile(package_folder, deps_folder, stdlib, cpp, libclang, output_folder):
    """Compiles files."""
    print_bar('Compiling')

    try:
        program = Program(
            package=get_package_from_path(package_folder / 'package.toml'),
            deps_folder=deps_folder,
            stdlib=stdlib,
            c_preprocessor=cpp,
            libclang=libclang
        )
        program_errors = program.compile(output_folder=output_folder)
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
        type=lambda p: Path(p).absolute().expanduser(),
        help='Package to compile',
        default=Path('.').absolute(),
        dest='package'
    )
    parser.add_argument(
        '--deps-folder',
        type=Path,
        help='Folder containing dependency packages',
    )
    parser.add_argument(
        '--stdlib',
        type=Path,
        required=True,
        help='Folder containing the Sylva standard library package'
    )
    parser.add_argument(
        '--output-folder', type=Path, required=True, help='Output folder'
    )
    parser.add_argument(
        '--cpp',
        type=Path,
        required=True,
        help='Path to C preprocessor executable'
    )
    parser.add_argument(
        '--libclang', type=Path, help='Path to libclang library'
    )
    parser.add_argument(
        '--only-parse', action='store_true', help='Only perform parsing'
    )

    args = parser.parse_args()

    if args.deps_folder is None:
        args.deps_folder = args.package / 'deps'

    if args.only_parse:
        parse(
            args.package,
            args.deps_folder,
            args.stdlib,
            args.cpp,
            args.libclang
        )
    else:
        compile(
            args.package,
            args.deps_folder,
            args.stdlib,
            args.cpp,
            args.libclang,
            args.output_folder
        )


if __name__ == '__main__':
    run()
