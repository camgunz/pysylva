import distutils.util
import os

from pprint import pprint


_DEBUG = distutils.util.strtobool(os.environ.get('SYLVA_DEBUG', 'no'))


def debugging():
    return _DEBUG


def debug(s):
    if not debugging():
        return
    if isinstance(s, str):
        print(s)
    else:
        pprint(s)
