"""
Emit parameters to pip extracted from a script.
"""

import sys

from .scripts import DepsReader


def run(args=None):
    """
    >>> run(['examples/test-mongodb-covered-query.py'])
    pytest jaraco.mongodb>=3.10
    """
    (script,) = args or sys.argv[1:]
    deps = DepsReader.try_read(script)
    print(' '.join(deps.params()))


__name__ == '__main__' and run()
