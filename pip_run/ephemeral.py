import contextlib
import tempfile
import shutil
import pathlib


@contextlib.contextmanager
def context(args):
    target = pathlib.Path(tempfile.mkdtemp(prefix='pip-run-'))
    try:
        yield target
    finally:
        shutil.rmtree(target)
