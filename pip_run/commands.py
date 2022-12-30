import os
import pathlib
import contextlib
import argparse

from more_itertools import split_before, split_at, padded

from ._py38compat import files


def _separate_script(args):
    """
    Inject a double-dash before the first arg that appears to be an
    extant Python script.

    >>> _separate_script(['foo', 'bar'])
    (['foo', 'bar'], [])
    >>> _separate_script(['foo', 'pip-run.py', 'bar'])
    (['foo'], ['pip-run.py', 'bar'])
    >>> _separate_script(['path.py', 'pip-run.py'])
    (['path.py'], ['pip-run.py'])
    >>> _separate_script(['README.rst'])
    (['README.rst'], [])
    """

    def is_extant_path(item: 'os.PathLike[str]'):
        path = pathlib.Path(item)
        return path.is_file() and path.suffix == '.py'

    groups = split_before(args, is_extant_path, maxsplit=1)
    return tuple(padded(groups, [], 2))


def _separate_dash(args):
    """
    Separate args based on a dash separator.

    >>> _separate_dash(['foo', '--', 'bar'])
    (['foo'], ['bar'])

    >>> _separate_dash(['foo', 'bar', '--'])
    (['foo', 'bar'], [])

    >>> _separate_dash(['foo', 'bar'])
    Traceback (most recent call last):
    ...
    ValueError: ...
    """
    pre, post = split_at(args, '--'.__eq__, maxsplit=1)
    return pre, post


def separate(args):
    """
    Separate the command line arguments into arguments for pip
    and arguments to Python.

    >>> separate(['foo', '--', 'bar'])
    (['foo'], ['bar'])
    >>> separate(['foo', 'bar'])
    (['foo', 'bar'], [])
    """
    with contextlib.suppress(ValueError):
        return _separate_dash(args)

    return _separate_script(args)


def intercept(args):
    """
    Detect certain args and intercept them.
    """
    usage = files(__package__).joinpath('usage.txt').read_text()
    argparse.ArgumentParser(usage=usage).parse_known_args(args)
