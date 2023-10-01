import contextlib
import tempfile
import pathlib


@contextlib.contextmanager
def context(args):
    with tempfile.TemporaryDirectory(prefix='pip-run-') as td:
        yield pathlib.Path(td)
