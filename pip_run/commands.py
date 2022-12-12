import os
import textwrap
import pathlib
import contextlib
import warnings

from more_itertools import split_before, split_at


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
    return next(groups), next(groups, [])


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


def parse_script_args(args):
    """
    Separate the command line arguments into arguments for pip
    and arguments to Python.
    """
    with contextlib.suppress(ValueError):
        return _separate_dash(args)

    return _separate_script(args)


def separate_dash(args):
    """
    Separate args based on dash separator.

    Deprecated; retained for compatibility.

    >>> separate_dash(['foo', '--', 'bar'])
    (['foo'], ['bar'])

    >>> separate_dash(['foo', 'bar'])
    [['foo', 'bar'], []]
    """
    warnings.warn("separate_dash is deprecated", DeprecationWarning)
    with contextlib.suppress(ValueError):
        return _separate_dash(args)
    return [args, []]


help_doc = textwrap.dedent(
    """
    Usage:

    Arguments to pip-run prior to `--` are used to specify the requirements
    to make available, just as arguments to pip install. For example,

        pip-run -r requirements.txt "requests>=2.0"

    That will launch python after installing the deps in requirements.txt
    and also a late requests. Packages are always installed to a temporary
    location and cleaned up when the process exits.

    Arguments after `--` are passed to the Python interpreter. So to launch
    `script.py`:

        pip-run -- script.py

    For simplicity, the ``--`` may be omitted and Python arguments will
    be inferred starting with the first Python file that exists:

        pip-run script.py

    If the `--` is omitted or nothing is passed, the python interpreter
    will be launched in interactive mode:

        pip-run
        >>>

    For more examples and details, see https://pypi.org/project/pip-run.
    """
).lstrip()


def intercept(args):
    """
    Detect certain args and intercept them.
    """
    if '--help' in args or '-h' in args:
        print(help_doc)
        raise SystemExit(0)
