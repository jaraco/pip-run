"""
Emit parameters to pip extracted from a script.
"""

import os

import autocommand

from .scripts import DepsReader


class ExtantFile(str):
    def __init__(self, value):
        if not os.path.isfile(value):
            raise FileNotFoundError(f"{value} does not exist.")


@autocommand.autocommand(__name__)
def run(script: ExtantFile):
    """
    >>> run(['examples/test-mongodb-covered-query.py'])
    pytest jaraco.mongodb>=3.10
    >>> run(['does-not-exist'])
    Traceback (most recent call last):
    FileNotFoundError: does-not-exist does not exist.
    """
    print(' '.join(DepsReader.try_read(script).params()))
