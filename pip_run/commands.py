import pathlib
import contextlib
import argparse
import shlex

from more_itertools import locate, split_at
from jaraco.functools import bypass_when
from jaraco import env  # type: ignore # (python/mypy#15970)

from ._py38compat import files


def _is_python_arg(item: str):
    """
    Return True if the item can be inferred as a parameter
    to Python and not to pip install.
    """
    path = pathlib.Path(item)
    # start with the tests which do very minimal IO
    if not path.exists():
        return False
    if path.suffix == ".py":
        return True

    # now, sniff the first line of the file and return true if it looks like a
    # python script based on the shebang line
    return _has_python_shebang(path)


def _has_python_shebang(path: pathlib.Path) -> bool:
    try:
        with path.open('rb') as fp:
            first_line_bytes = fp.readline()
        first_line = first_line_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return False
    if not first_line.startswith('#!'):
        return False

    cmd = shlex.split(first_line[2:])
    if cmd[0] == "/usr/bin/env":
        cmd = cmd[1:]
        if cmd[0] == "-S":
            cmd = cmd[1:]
        command_name = cmd[0]
    else:
        command_name = cmd[0].split('/')[-1]

    return command_name in (
        "python",
        "pip-run",
        "py",
        "python3",
        "pypy",
        "pypy3",
    ) or command_name.startswith("python3.")


def _separate_script(args):
    """
    Split arguments into install and python args based on inferenece.

    >>> _separate_script(['foo', 'bar'])
    (['foo', 'bar'], [])
    >>> _separate_script(['foo', 'pip-run.py', 'bar'])
    (['foo'], ['pip-run.py', 'bar'])
    >>> _separate_script(['path.py', 'pip-run.py'])
    (['path.py'], ['pip-run.py'])
    >>> _separate_script(['path.py', 'pip-run.py', 'pip-run.py'])
    (['path.py'], ['pip-run.py', 'pip-run.py'])
    >>> _separate_script(['README.rst'])
    (['README.rst'], [])
    >>> _separate_script(['pip-run.py'])
    ([], ['pip-run.py'])
    >>> _separate_script(['pip-run.py', 'pip-run.py'])
    ([], ['pip-run.py', 'pip-run.py'])
    """
    pivot = next(locate(args, _is_python_arg), len(args))
    return args[:pivot], args[pivot:]


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


@bypass_when(env.Check('PIP_RUN_IPYTHON_MODE', default='infer', expect='ignore'))
def infer_ipython(sep_args):
    """
    Check for the presence of the argument 'ipython' in pip_args.

    If present and py_args is empty, return arguments for pip and
    Python that when run will start an ipython interpreter.

    >>> infer_ipython((['ipython', 'foo'], []))
    (['ipython', 'foo'], ['-m', 'IPython'])
    >>> infer_ipython((['ipython', 'foo'], ['bar']))
    (['ipython', 'foo'], ['bar'])
    >>> infer_ipython((['foo'], ['bar']))
    (['foo'], ['bar'])

    >>> getfixture('monkeypatch').setenv('PIP_RUN_IPYTHON_MODE', 'ignore')
    >>> infer_ipython((['ipython', 'foo'], []))
    (['ipython', 'foo'], [])
    >>> getfixture('monkeypatch').setenv('PIP_RUN_IPYTHON_MODE', 'infer')
    >>> infer_ipython((['ipython', 'foo'], []))
    (['ipython', 'foo'], ['-m', 'IPython'])
    """
    pip_args, py_args = sep_args
    use_ipython = not py_args and 'ipython' in pip_args

    return (
        pip_args,
        ['-m', 'IPython'] * use_ipython + py_args,
    )


def intercept(args):
    """
    Detect certain args and intercept them.
    """
    usage = files(__package__).joinpath('usage.txt').read_text(encoding='utf-8')
    argparse.ArgumentParser(usage=usage).parse_known_args(args)
