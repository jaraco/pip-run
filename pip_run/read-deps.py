"""
Emit parameters to pip extracted from a script.
"""

import pathlib

import autocommand
import path

from .scripts import DepsReader


def separator(input) -> str:
    lookup = dict(space=' ', newline='\n', null='\0')
    return lookup.get(input, input)


@autocommand.autocommand(__name__)
def run(
    script: path.ExtantFile,
    separator: separator = ' ',  # type: ignore
):
    """
    >>> run(['examples/test-mongodb-covered-query.py'])
    pytest jaraco.mongodb>=3.10
    >>> run(['does-not-exist'])
    Traceback (most recent call last):
    FileNotFoundError: does-not-exist does not exist as a file.
    >>> run(['examples/test-mongodb-covered-query.py', '--separator', 'newline'])
    pytest
    jaraco.mongodb>=3.10
    """
    joiner = separator.join  # type: ignore
    print(joiner(DepsReader.try_read(pathlib.Path(script)).params()))
