import ctypes
import os

from pprint import pprint


_DEBUG = [x.strip() for x in os.environ.get('SYLVA_DEBUG', '').split(',')]
_SIZE_SIZE = ctypes.sizeof(ctypes.c_size_t) * 8


def debugging(tag=None):
    return bool(_DEBUG) and (tag is None or tag in _DEBUG)


def debug(tag, s):
    if tag not in _DEBUG:
        return

    if isinstance(s, str):
        print(s)
    else:
        pprint(s)
