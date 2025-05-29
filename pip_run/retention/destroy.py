import contextlib
import pathlib
import tempfile

from ..compat import py39


@contextlib.contextmanager
def context(args):
    with tempfile.TemporaryDirectory(
        prefix='pip-run-', **py39.ignore_cleanup_errors
    ) as td:
        yield pathlib.Path(td)
