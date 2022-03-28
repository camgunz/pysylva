import os

from pprint import pprint


_DEBUG = [x.strip() for x in os.environ.get('SYLVA_DEBUG', '').split(',')]


def debugging():
    return bool(_DEBUG)


def debug(tag, s):
    if not tag in _DEBUG:
        return

    if isinstance(s, str):
        print(s)
    else:
        pprint(s)
