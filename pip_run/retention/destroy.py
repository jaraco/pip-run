import contextlib
import pathlib
import tempfile


@contextlib.contextmanager
def context(args):
    with tempfile.TemporaryDirectory(prefix='pip-run-') as td:
        yield pathlib.Path(td)
