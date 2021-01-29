"""
Emit parameters to pip extracted from a script.
"""

import autocommand
import path

from .scripts import DepsReader


@autocommand.autocommand(__name__)
def run(script: path.ExtantFile):
    """
    >>> run(['examples/test-mongodb-covered-query.py'])
    pytest jaraco.mongodb>=3.10
    >>> run(['does-not-exist'])
    Traceback (most recent call last):
    FileNotFoundError: does-not-exist does not exist as a file.
    """
    print(' '.join(DepsReader.try_read(script).params()))
