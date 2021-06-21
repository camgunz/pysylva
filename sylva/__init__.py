import distutils.util
import os

from pprint import pprint


def is_debugging():
    _DEBUG = distutils.util.strtobool(os.environ.get('SYLVA_DEBUG', 'no'))


def debug(s):
    if not is_debugging():
        return
    if isinstance(s, str):
        print(s)
    else:
        pprint(s)
